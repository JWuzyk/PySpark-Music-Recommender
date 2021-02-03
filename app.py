from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import json
import pickle
import os
import random

#Flask
app = Flask(__name__)

#Setup SQLALchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recommendations.db'
db = SQLAlchemy(app)

#Defunct database setup
# class Tracks(db.Model):
#     __tablename__ = 'Tracks'
#     track_id = db.Column(db.Integer(), primary_key = True)
#     track = db.Column(db.String(100), nullable = False)
#     artist = db.Column(db.String(100), nullable = False)

#     def __repr__(self):
#     	return f'{self.tarck} by {slef.artist}'

# class Recommendations(db.Model):
#     __tablename__ = 'Recommendations'
#     index = db.Column(db.Integer(), primary_key = True)
#     track_id = db.Column(db.String(100), nullable = False)
#     recommended_id = db.Column(db.String(100), nullable = False)
#     dist = db.Column(db.Float(), nullable = False)    
#     def __repr__(self):
#         return f'({self.track_id},{self.recommended_id},{dist})'


#load name_to_id dict to do id lookups
#TODO: Replace with database lookups
with open('name_to_id.json', 'rb') as d:
    name_to_id = json.load(d)
    id_to_name = {v:k for k,v in name_to_id.items()}


#Main request
@app.route('/', methods = ['GET','POST'])
def enter_rec(invalid = False):

    #When Button pressed
    if request.method == 'POST':

        #Recommending from entered values button press
        if 'get_rec' in request.form:
            
            #get artist and track name
            artist = request.form['artist'].strip()
            track_name = request.form['track'].strip()

            #Get full name for id lookup and get id
            full_name = artist +'-'+ track_name
            if full_name  in name_to_id:
                idx = name_to_id[full_name] 
            else:
                #If song not found
                return render_template('main.html',invalid=True, recs = [],len=0, searched = [])

        #Random prediction button press
        elif 'rand' in request.form:
            idx = random.randint(0,len(name_to_id))
            artist = id_to_name[idx].split('-')[0]
            track_name = id_to_name[idx].split('-')[1]


        searched = (artist,track_name) #Save searched for artist and track

        #Added option for stoping returning same artist since many songs have recommendations by the same artist
        allow_same_artist = (request.form.get('same_artist') == 'allow') # Get value from checkbox

        recs = get_rec(idx,searched, allow_same_artist)
        return render_template('main.html',invalid=False, recs = recs, len = len(recs), searched = searched)
    else:
        return render_template('main.html',invalid=False, recs = [],len=0, searched = [])

  
def get_rec(track_id, searched,allow_same_artist = False):

    if allow_same_artist:
        #Get top 5 recommendations for the song with id track_id
        result = db.engine.execute("SELECT Tracks.artist, Tracks.track \
        FROM (SELECT recommended_id, distance FROM Recommendations WHERE track_id = ?) AS Recommended\
        INNER JOIN Tracks WHERE Tracks.track_id = Recommended.recommended_id \
        ORDER BY Recommended.distance LIMIT 5", (track_id,))
    else:
        artist = searched[0]
        #Get top 5 recommendations for the song with id track_id with different artists
        result = db.engine.execute("SELECT Tracks.artist, Tracks.track \
        FROM (SELECT recommended_id, distance FROM Recommendations WHERE track_id = ?) AS Recommended\
        INNER JOIN Tracks WHERE Tracks.track_id = Recommended.recommended_id AND Tracks.artist  <> ? \
        ORDER BY Recommended.distance LIMIT 5", (track_id, artist))

    return list(result)


if __name__ == '__main__':
	app.run(debug = False, host='0.0.0.0') #uncomment to run not locally
    #app.run(debug = True) #uncomment to run locally