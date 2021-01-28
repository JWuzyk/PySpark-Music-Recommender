import numpy as np
import pandas as pd
import os
import json
import csv

from pyspark import SparkContext
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

from pyspark.sql.functions import lit,concat,col
from pyspark.ml.feature import StringIndexer
from pyspark.sql.types import IntegerType
from time import time


from pyspark.mllib.recommendation import ALS, MatrixFactorizationModel, Rating

def train_model(dataset_loc = 'spotify_dataset.csv', model_loc = "CollaborativeFilterModel", max_len = int(1e4)):

    max_len = max_len
    csv_name = dataset_loc
    #Start Spark session
    os.environ['JAVA_HOME'] = r"C:\Program Files\Java\jdk-15.0.1" 
    spark = SparkSession.builder.master('local[*]').appName("Reccomender").getOrCreate()

    #Read Data
    df = spark.read.option("header", "true").schema('user string, artist string, track string, playlist string').csv(csv_name).limit(max_len)
    df = df.na.drop()

    #Add unique name column from concatenating artist and track name
    df = df.withColumn('count',lit(1)).withColumn('full_name', concat(col('artist'),lit(' '), col('track')))
        
    #Get unqiue ids for each playlist and track
    indexer_pl = StringIndexer(inputCol="playlist", outputCol="playlist_id")
    df = indexer_pl.fit(df).transform(df)

    indexer_t = StringIndexer(inputCol="track", outputCol="track_id")
    df = indexer_t.fit(df).transform(df)

    df = df.withColumn("track_id", df["track_id"].cast(IntegerType()))
    df = df.withColumn("playlist_id", df["playlist_id"].cast(IntegerType()))

    #Get dictionaries to translate from track name to id
    id_to_name = df.select('full_name','track_id').distinct().toPandas().to_dict(orient='index')
    id_to_name = {k : v['full_name'] for k,v in id_to_name.items()}
    name_to_id = {v : k for k,v in id_to_name.items()}

    #Save translation dicts
    with open('name_to_id.json', 'w') as f:
        json.dump(name_to_id, f)

    with open('id_to_name.json', 'w') as f:
        json.dump(id_to_name, f)




    num_tracks = df.select('track_id').distinct().count()
    num_playlists = df.select('playlist_id').distinct().count()

    with open('meta.json', 'w') as f:
        json.dump({'num_playlists':num_playlists, 'num_tracks':num_tracks}, f)

    #Add fake playlists only containing one played track to get reccomendations for that track
    df_extra = spark.createDataFrame([((num_playlists+i),i,1) for i in range(num_tracks)],['playlist_id','track_id','count'])

    #Get ratings dataframe
    ratings = df.select('playlist_id','track_id','count')
    #Add fake playlists
    ratings = ratings.union(df_extra).rdd


    #https://spark.apache.org/docs/latest/mllib-collaborative-filtering.html#collaborative-filtering

    # Build the recommendation model using Alternating Least Squares
    rank = 10
    numIterations = 10
    model = ALS.train(ratings, rank, numIterations)

    # Evaluate the model
    testdata = ratings.map(lambda p: (p[0], p[1]))
    predictions = model.predictAll(testdata).map(lambda r: ((r[0], r[1]), r[2]))
    ratesAndPreds = ratings.map(lambda r: ((r[0], r[1]), r[2])).join(predictions)
    MSE = ratesAndPreds.map(lambda r: (r[1][0] - r[1][1])**2).mean()
    print("Mean Squared Error = " + str(MSE))

    pred = model.recommendProductsForUsers(5).map(lambda x: (x[0],x[1][0][1],x[1][1][1],x[1][2][1],x[1][3][1],x[1][4][1])).collect()

    pred = [[id_to_name[i] for i in p] for p in pred]
    print(pred)


    with open('pred.json', 'w') as f:
        json.dump({'pred':pred}, f)

    #Save model
    #model.save(spark.sparkContext,model_loc)

def reccomend(rec_id,model_loc,num_rec=5):
    with open('id_to_name.json', 'rb') as f:
        id_to_name = json.load(f)

    with open('meta.json', 'rb') as f:
        meta = json.load(f)

    os.environ['JAVA_HOME'] = r"C:\Program Files\Java\jdk-15.0.1" 
    spark = SparkSession.builder.getOrCreate()
    model = MatrixFactorizationModel.load(spark.sparkContext,model_loc)

    num_playlists = meta['num_playlists']


    pred = model.recommendProducts(num_playlists+rec_id,num_rec)
    print(id_to_name[str(rec_id)])
    print([id_to_name[str(pred[i][1])] for i in range(num_rec)])


train_model()
#reccomend(100,"CollaborativeFilterModel")
