#!/usr/bin/env python
# coding: utf-8

import pandas as pd


movies = pd.read_csv("data/movies_converted.csv")
movies = movies[["id", "title", "overview", "genres"]]

movies.loc[:, "tags"] = movies["overview"] + ' ' + movies["genres"] 

new_data = movies.drop(columns=["overview", "genres"])


cv = CountVectorizer(stop_words="english")
vector = cv.fit_transform(new_data["tags"].values.astype("U"))

vector = vector.toarray()

similarity = cosine_similarity(vector)
distance = sorted(list(enumerate(similarity[238])), reverse=True, key=lambda vector:vector[1])


similarity.dump(open("similarity.pkl", "wb"))
pickle.dump(new_data, open("movies_list.pkl", "wb"))