from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import json
import pickle
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reccomendations.db'
db = SQLAlchemy(app)

class Reccomendations(db.Model):
    __tablename__ = 'top_one'
    track_id = db.Column(db.Integer(), primary_key = True)
    track = db.Column(db.String(100), nullable = False)
    rec = db.Column(db.String(100), nullable = False)
    def __repr__(self):
    	return f'If you like {self.track} you should listen to  {self.rec}'

with open('name_to_id.json', 'rb') as d:
    name_to_id = json.load(d)
    id_to_name = {v:k for k,v in name_to_id.items()}


def predict(rec_id):
    Reccomendations.query.filter_by(track_id=rec_id).first()
    return pred

@app.route('/', methods = ['GET','POST'])
def enter_rec(invalid = False):

    if request.method == 'POST':
        artist = request.form['artist']
        track_name = request.form['track']
        full_name = artist +'-'+ track_name
        print(full_name)
        if full_name  in name_to_id:
            idx = name_to_id[full_name]
            return redirect(f'/reccomendation/{idx}')
        else:
            return render_template('main.html',invalid=True)
        
    else:
        return render_template('main.html',invalid=False)
    


@app.route('/reccomendation/<int:id>')
def get_rec_page(id):
    try:
        rec = Reccomendations.query.get_or_404(id)
        return render_template('result.html', rec = rec)
    except:
        return f"Not Found {id}"
    

if __name__ == '__main__':
	app.run(debug = True, host='0.0.0.0')