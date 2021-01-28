from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import json
import pickle
import os

from pyspark.mllib.recommendation import ALS, MatrixFactorizationModel, Rating
from pyspark.sql import SparkSession
app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pred.db'
# db = SQLAlchemy(app)


# class Reccomendations(db.Model):
# 	track_id = db.Column(db.Integer(), primary_key = True)
# 	artist = db.Column(db.String(100), nullable = False)
# 	track_name = db.Column(db.String(100), nullable = False)
# 	r1 = db.Column(db.Integer(), nullable = False)
# 	r2 = db.Column(db.Integer(), nullable = False)
# 	r3 = db.Column(db.Integer(), nullable = False)
# 	r4 = db.Column(db.Integer(), nullable = False)
# 	r5 = db.Column(db.Integer(), nullable = False)

# 	def __repr__():
# 		return f'Track: {self.track_id}: {self.track_name} by {self.artist} '

# presistent = 0

# @app.route('/test', methods = ['GET','POST'])
# def test():
#     global presistent
#     presistent += 1
#     return str(presistent)

with open('name_to_id.json', 'rb') as d:
    name_to_id = json.load(d)

with open('id_to_name.json', 'rb') as d:
    id_to_name = json.load(d)

with open('meta.json', 'rb') as f:
    meta = json.load(f)

 
os.environ['JAVA_HOME'] = r"C:\Program Files\Java\jdk-15.0.1"    
spark = SparkSession.builder..master('local[*]').appName("Reccomender").getOrCreate()
sc = spark.sparkContext

model_loc = "CollaborativeFilterModel"
model = MatrixFactorizationModel.load(sc,model_loc)

model.userFeatures().cache()
model.productFeatures().cache()

num_playlists = meta['num_playlists']


def predict(rec_id,num_rec=5):
    pred = model.recommendProducts(num_playlists+rec_id,num_rec)
    return pred

@app.route('/', methods = ['GET','POST'])
def hello_world(invalid = False):

    if request.method == 'POST':
        artist = request.form['artist']
        track_name = request.form['track']



        full_name = artist + track_name

        if full_name  in name_to_id:
            idx = name_to_id[full_name]
            return redirect(f'/reccomendation/{idx}')
        else:
            return render_template('main.html',invalid=True)
        
    else:
        return render_template('main.html',invalid=False)
    


@app.route('/reccomendation/<int:id>')
def get_rec_page(id):
    #rec = Reccomendations.query.get_or_404(id)
    #if rec:
    #    return render_template('result.html', rec = rec)        
    # else
    #     #load model
    #     #model.predict(...)
    #     #Add to db
    #     return render_template('result.html', rec = 'In progress')
    
    pred = [id_to_name[str(p[1])] for p in predict(id)]
    return str(pred)
    

if __name__ == '__main__':
	app.run(debug = True)


    # predict
    # cache