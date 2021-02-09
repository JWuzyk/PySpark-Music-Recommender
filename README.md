# PySpark-Music-Recommender
An app to recommend you news song based on ones you like.

I extracted a list of songs and playlists they appeared in from a spotify playlist dataset (https://zenodo.org/record/2594557#.YBfn5ehKhPY). I then used item-based collaborative filtering to get similar songs to the searched one. This was done using an MinHash implemented in PySpark. The resulting recommendations were then saved to a SQL database. I then made a flask app which allows users to enter an artist and song name and then returns recommendations from the SQL database. I then created a docker image for this app and deployed this image to a google cloud VM. You can acces the site at: http://35.187.177.117:5000/  (temporary).

The goal of creating this app was to learn new skills (PySpark, Reccomender Systems) and learn the (very) basics of how to deploy an app (Flask, docker, cloud).

Technologies used:
  - Pandas
  - PySpark
  - Flask
  - SQL
  - Docker
  - Google Cloud


# Some Relevant Concepts
Here I give a brief overview of some of the concepts I use. This is not meant to be indepth and only covers some basic ideas.
## Recommender Systems

A common problem in for many companies is helping users connect users with the itmes they find valuable whether it is a song they will like, a new jacket or an old friend from high school. The use of the internet and the general trend towards big data has given companies masses of data about their users and their activity and preferences. The goal of a recommender system is to leverage this data to give good recommendations.

There are two main kinds of recommender systems: Collaborative Filtering and Content-Based Filtering.

Briefly, collaborative filtering uses users' activity, e.g. You like a lot of the same movies as my other friend and they like this one so you probably will aswell. On the other hand, content-based filtering uses properties of the items themselves and users preferences for them e.g. You like action movies and the actor Dwayne Johnson so you will probably like the latest The Fast and the Furious movie (An action movie starting Dwayne Johnson). Another option and quite often the best one is a Hybrid approach combining both of these ideas. That said this app only uses collaborative filtering and I focus on that from here onwards.

## Collaborative Filtering
There are two common forumaltions of collaborative filtering with slightly different goals: user-based and item-based.

Generally for user-based collaborative filtering we have a set of users U = {u_1 .. u_n},a set of items I = {i_1 .. i_m } and we a generally incomplete matrix of ratings of items (k) by users (j), R = {r_jk}. The problem is then to estimate the missing ratings. We can then use these infered ratings to suggest new items to users. Often we do not have actually ratings but rather implicit measurements such as views or purchases. A common approach to this problem is matrix factorization where we assume that the full matrix R can be factored as a product of two lower rank matrices U and V. In general this is not possible exactly but we can calculate candidates for U and V by minimizing the reconstruction error on the know values on R. We can then use this U and V to infer values for unknown ratings. A common algorithm to do this minimization is Alternating Least Squares.

Generally for item-based collaborative filtering, we again have a set of items I = {i_1 .. i_m } and a set of users U = {u_1 .. u_n} and we a matrix of (implicit or explicit) ratings of items (j) by users (k), R = {r_jk}. Now instead we recommend new items based on their similarity to a given item. This can be done using various similarity measures for example cosine similarity or jaccard similarity. A naive approach to this is to simply compute the similarity between your given item and every other item in our data set and then give the nearest items as recommendations. Unfortunatley this quickly becomes untenable with large high dimensional datasets. A attempt to make this approach deasible is described in the next section.

Some general issues with collaborative filtering are that it can't deal with unseen data (How do we know what people think of a song if no one has ever heard it?) and the sheer volume of data it can generate. 

## Approximate Nearest Neighbours

In general given N items with D features, a simple nearest neighbours algorithm works in O(ND) time. For many algorithms this wouldn't seem that bad but given the sheer size of datasets in this field, for example spotify has over 50 million songs and over 200 million users, we need faster a faster algorithm to make this approach even slightly practical. This is where approximate nearest neighbours comes in. While the naive algorithm can be improved for low dimensional data none of these approaches scale well into higher dimensions. The solution is, instead of looking for an exact answer we allow approximate answers. Formally given a collection of items p_i, a given item q and c > 1 we find p such that d(p,q) < c min_i d(p_i,q_i) instead of d(p,q) = min_i d(p_i,q_i). To do this we use the idea of hash functions.

### Locally Senstive Hashing
A locally senstive hash function is one such that if two items are near each other they end up in the same bucket with high probability and if they are far from each other they end up in different buckets. Formally gievm (r, cr, p1, p2) where r = min_p d(p_i,q), c>1 and p1 >= p2 are probabilities a hash function h(x) is a LSH fucntion if:

P[h(x) = h(y)] >p1 if d(x,y) < r

P[h(x) = h(y)] < p2 if d(x,y) > cr

We can then leverage a family of such a family of hash functions to give us a approximate solution by tuning the probabilities by concatenating hashes and adding more tables.

Since in this app we approximate Jaccard similarity we leverage a family of hash functions call Min Hashing.

See http://web.stanford.edu/class/cs369g/files/lectures/lec16.pdf for silightly more details.

