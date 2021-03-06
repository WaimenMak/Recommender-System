# -*- coding: utf-8 -*-
# @Time    : 2022/3/31 22:11
# @Author  : Weiming Mai
# @FileName: algo2.py
# @Software: PyCharm


import pandas as pd
import numpy as np
import random
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
# from processing import preprocessing
import csv
import json
from .content_based_recommendation import user_add_content_based_approach

times = 0

def user_add(iid, score):
    user = '944'
    # simulate adding a new user into the original data file
    df = pd.read_csv('./u.data')
    df.to_csv('new_' + 'u.data')
    with open(r'new_u.data',mode='a',newline='',encoding='utf8') as cfa:
        wf = csv.writer(cfa,delimiter='\t')
        data_input = []
        s = [user,str(iid),int(score),'0']
        data_input.append(s)
        for k in data_input:
            wf.writerow(k)

def store_result(store_list, mid, title, exp, poster, origin, sim):
  entry = {
      "movie_id": int(mid),
      "movie_title": title,
      "score": 0,
      "poster_url": poster,
      "explaination": exp,
      "origin": origin,
      "sim": sim
  }
  store_list.append(entry)
  return store_list

def item2vec(movies, data, model, user_id, init_set, n, round):
    print("item2vec")
    # iid = str(sorted(movies, key=lambda i: i.score, reverse=True)[0].movie_id)
    # score = int(sorted(movies, key=lambda i: i.score, reverse=True)[0].score)
    if round > 1:
        global times
        times += 1
        print("now next round")
        finetune_model(movies, model)
        print("out")

    # iid = str(sorted(movies, key=lambda i: i['score'], reverse=True)[0]['movieId'])
    # score = int(sorted(movies, key=lambda i: i['score'], reverse=True)[0]['score'])

    # user_add(iid, score)
    user_add_content_based_approach(movies, user_id, round, 2)
    # s = set()
    ls = []
    not_interest = []
    for movie in movies:
      # if movie.score >= 4:
        not_interest.append(movie.movie_id)
        if movie.score >= 4:
        # sim = model.most_similar([str(movie.movieId)], topn=10)
            print(str(movie.movie_id))
            sim = model.wv.most_similar([str(movie.movie_id)], topn=20)
            for item in sim:
                # print(item[0])
                # if item[1] < 0.7:
                #     continue
                if int(item[0]) in not_interest:
                    continue
                if len(data[data["movie_id"] == int(item[0])]) > 0:
                    title = data.loc[data['movie_id']==int(item[0]),'movie_title'].values[0]
                    exp = f"Your interested movie: {movie.movie_title} has {item[1]:.2f} similarity to movie: {title}"
                    poster = data.loc[data['movie_id']==int(item[0]),'poster_url']
                    origin = data.loc[data['movie_id']==movie.movie_id,'poster_url']
                  # s.add(item[0])
                    store_result(ls, item[0], title, exp, poster, origin, item[1])
                  # recommendation = temp.loc[temp['movieId']==item[0]]
    ls = sorted(ls, key=lambda e: e.__getitem__('sim'), reverse=True)
    m = len(ls)
    print(m)

    if m > n:
        # res = np.random.choice(list(s), n)
        # res = random.sample(ls, n)
        try:
            res = ls[times*n: times*n + n]
            print(f"times{times}")
        except:
            res = random.sample(ls, n)
            print("sample")
        results = pd.DataFrame(res)
        results = results.sort_values(by="sim", ascending=False)
        print("res1")
        return json.loads(results.to_json(orient="records"))
    elif m < n and m > 0:
        results = pd.DataFrame(ls)
        results = results.sort_values(by="sim", ascending=False)
        print("res2")
        return json.loads(results.to_json(orient="records"))
    elif m == 0:
        res = np.random.choice(list(init_set), n)
        res = [int(i) for i in res]
        rec_movies = data.loc[data['movie_id'].isin(res)]
        # print(rec_movies)
        rec_movies.loc[:, 'score'] = 0
        rec_movies.loc[:, 'origin'] = None
        rec_movies.loc[:, 'explaination'] = "Choosen from your keywords"
        results = rec_movies.loc[:, ['movie_id', 'movie_title', 'poster_url', "explaination", "origin"]]
        return json.loads(results.to_json(orient="records"))

def finetune_model(movies, model):
    """
    The following round of recommendation would produce some new training data according to the users' like and dislike,
    that can be separated  as two sentences.
    :param movies: List of movies
    :param model: The pretrained word2vec model
    :return: Updated model parameters
    """
    interested = []
    not_interested = []

    for movie in movies:
        if movie.score >= 4:
            interested.append(str(movie.movie_id))
            print("interest")
        else:
            not_interested.append(str(movie.movie_id))
            print("not interest")
    if len(interested) > 0 or len(not_interested) > 0:
        new_sentense = [interested, not_interested]
        model.train(new_sentense, total_examples=model.corpus_count, epochs=model.epochs)

def item2vec_get_items(iid, data, model):
    res = model.wv.most_similar([str(iid)], topn=5)
    res = [int(item[0]) for item in res]
    rec_movies = data.loc[data['movie_id'].isin(res)]
    print(rec_movies)
    rec_movies.loc[:, 'score'] = 0

    rec_movies.loc[:, 'origin'] = data.loc[data['movie_id']==iid,'poster_url']
    rec_movies.loc[:, 'explaination'] = "5 most similar movies"
    results = rec_movies.loc[:,  ['movie_id', 'movie_title', 'poster_url', "score", "explaination", "origin"]]
    return json.loads(results.to_json(orient="records"))


# @app.post("/api/refresh")
# def refresh_movies():
#     """
#     refresh the movies after clicking the refresh button
#     :return:
#     """
#     res = np.random.choice(list(init_set), 18)
#     results = data[data['movieId'].isin(res)]
#     print(results)
#     return json.loads(results.to_json(orient="records"))
