# PySpark-Music-Recommender (In progress)
An app to recommend you news song based on ones you like.

The goal of creating this app was to learn new skills (PySpark, Reccomender Systems) and learn the (very) basics of how to deploy an app (Flask, docker, cloud).

I extracted a list of songs and playlists they appeared in from a spotify playlist dataset (https://zenodo.org/record/2594557#.YBfn5ehKhPY). I then used item-item collaborative filtering to get similar songs to the searched one. This was done using an approximate similarity join implemented in PySpark. The resulting recommendations were then saved to a SQL database. I then made a flask app which allows users to enter an artist and song name and then returns recommendations from the SQL database. I then created a docker image for this app and deployed this image to a google cloud VM. You can acces the site at: http://35.187.177.117:5000/  (temporary).

Technologies used:
  - Pandas
  - PySpark
  - Flask
  - SQL
  - Docker
  - Google Cloud
