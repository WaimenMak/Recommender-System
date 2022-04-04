from typing import Optional, List
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import numpy as np
import os
import csv
from sklearn.cluster import estimate_bandwidth
from surprise import Reader
from surprise.model_selection import train_test_split
from utils import map_genre
import json
from surprise import dump
from surprise import KNNBasic
from surprise import Dataset
from entities.Movie import Movie

from flask import Flask, render_template, g, jsonify, request, redirect, url_for, session, flash
import os

import  recommendationAlgorithms.content_based_recommendation as content_based

#Flask 
app = Flask(__name__,
            static_folder = "./dist/static",
            template_folder = "./dist")

## Fast API 
# templates = Jinja2Templates(directory="templates")     
     
# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# =======================DATA=========================
data = pd.read_csv("movie_info.csv")
genre_list =["Action", "Adventure", "Animation", "Children", "Comedy", "Crime","Documentary", "Drama", "Fantasy", "Film_Noir", "Horror", "Musical", "Mystery","Romance", "Sci_Fi", "Thriller", "War", "Western"]

"""
=================== Body =============================
"""

#=======================Website===============================
# @app.get("/test", response_class=HTMLResponse)
# async def read_item(request: Request):
#     return templates.TemplateResponse("/client/index.html",{"request": request}) 

# == == == == == == == == == API == == == == == == == == == == =



#== == == == == == == == == 1. Get Keywords/ Genres for initial selection  
# show four genres
@app.get("/api/genre")
def get_genre():
    return {'genre': ["Action", "Adventure", "Animation", "Children"]}

# show all generes
'''
@app.get("/api/genre")
def get_genre():
    return {'genre': ["Action", "Adventure", "Animation", "Children", "Comedy", "Crime",
                      "Documentary", "Drama", "Fantasy", "Film_Noir", "Horror", "Musical", "Mystery",
                      "Romance", "Sci_Fi", "Thriller", "War", "Western"]}
'''

#== == == == == == == == == 2. Get Keywords/ Genres for initial selection  
@app.post("/api/movies")
def get_movies(genre: list):
    print(genre)
    query_str = " or ".join(map(map_genre, genre))
    results = data.query(query_str)
    results.loc[:, 'score'] = None
    results = results.sample(18).loc[:, ['movie_id', 'movie_title', 'release_date', 'poster_url', 'score']]
    return json.loads(results.to_json(orient="records"))



#== == == == == == == == == 3. Get Recommendation
@app.post("/api/recommend")
def get_recommend(movies: List[Movie]):
    """
    ### Summary: 
    - this function is called each time a new recommendation is made -> as input a set of movies with ratings is provided 
    - depending on the specified algorithm either Algorithm 1 or Algorithm 2 is chose for the computation of the recommendation 
        - Algorithm 1: content-based algorithm with cosine similarity 
        - Algorithm 2: item to factor algorithm 

    Args:
        movies (List[Movie]): List of movies with ratings 
        algorithm: Which algorithm should be used to execute the function -> possible values: 0,1 
        user_id: id of the user that made the request 


    Returns:
        - Algorithm 1: 
            1. recommendationList: list with movie recommendations for the user 
            2. userProfile: user profile for the user 
        - Algorithm 2: 
            1. recommendationList: list with movie recommendations for the user 
            2. similarity Score:
        
    """     

    #TODO: at the moment the user id is hardcoded -> should be provided by the function call
    algorithm =1 
    if algorithm==1: 
        #Here the content based algorithm is called 
        recommendations, user_profile = content_based.get_recommend_content_based_approach(movies, data, genre_list, 944, 1)
    else: 
        #TODO: implement item-to-factor algorithm 
        pass
    return recommendations

#== == == == == == == == == 4. This returns the 5 most simlar items for a given item_id 
@app.get("/api/add_recommend/{item_id}")
async def add_recommend(item_id):
    """
    ### Summary: 
    - this function is called to retrieve the 5 most similar items 
    - depending on the specified algorithm either Algorithm 1 or Algorithm 2 is chose for the computation of the recommendation 
        - Algorithm 1: content-based algorithm with cosine similarity 
        - Algorithm 2: item to factor algorithm 

    Args:
        movies (List[Movie]): List of movies with ratings 
        algorithm: Which algorithm should be used to execute the function -> possible values: 0,1 
        user_id: id of the user that made the request 


    Returns:
        - Algorithm 1: 
            1. similarityList: 5 most similar items for a given algorithm 
        - Algorithm 2: 
            1. similarityList: 5 most similar items for a given algorithm 
        
    """     
    algorithm = 1
    if algorithm==1: 
        #Here the content based algorithm is called 
        result = content_based.get_similar_items_content_based_approach(item_id, data, genre_list, user_id=944)
    else: 
        #TODO: implement item-to-factor algorithm 
        pass
    return result

    # res = get_similar_items(str(item_id), n=5)
    # res = [int(i) for i in res]
    # print(res)
    # rec_movies = data.loc[data['movie_id'].isin(res)]
    # print(rec_movies)
    # rec_movies.loc[:, 'like'] = None
    # results = rec_movies.loc[:, ['movie_id', 'movie_title', 'release_date', 'poster_url', 'like']]
    # return json.loads(results.to_json(orient="records"))


# def user_add(iid, score):
#     user = '944'
#     # simulate adding a new user into the original data file
#     df = pd.read_csv('./u.data')
#     df.to_csv('new_' + 'u.data')
#     with open(r'new_u.data',mode='a',newline='',encoding='utf8') as cfa:
#         wf = csv.writer(cfa,delimiter='\t')
#         data_input = []
#         s = [user,str(iid),int(score),'0']
#         data_input.append(s)
#         for k in data_input:
#             wf.writerow(k)

# def get_initial_items(iid, score, n=12):
#     res = []
#     user_add(iid, score)
#     file_path = os.path.expanduser('new_u.data')
#     reader = Reader(line_format='user item rating timestamp', sep='\t')
#     data = Dataset.load_from_file(file_path, reader=reader)
#     trainset = data.build_full_trainset()
#     algo = KNNBasic(sim_options={'name': 'pearson', 'user_based': False})
#     algo.fit(trainset)
#     dump.dump('./model',algo=algo,verbose=1)
#     all_results = {}
#     for i in range(1682):
#         uid = str(944)
#         iid = str(i)
#         pred = algo.predict(uid,iid).est
#         all_results[iid] = pred
#     sorted_list = sorted(all_results.items(), key = lambda kv:(kv[1], kv[0]), reverse=True)
#     for i in range(n):
#         print(sorted_list[i])
#         res.append(sorted_list[i][0])
#     return res

# def get_similar_items(iid, n=12):
#     algo = dump.load('./model')[1]
#     inner_id = algo.trainset.to_inner_iid(iid)
#     print(inner_id)
#     neighbors = algo.get_neighbors(inner_id, k=n)
#     neighbors_iid = [algo.trainset.to_raw_iid(x) for x in neighbors]
#     print(neighbors_iid)
#     return neighbors_iid

# port = os.getenv('PORT', '5006')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8000,debug=True)