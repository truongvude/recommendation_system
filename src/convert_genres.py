#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import ast

data_movies = pd.read_csv("data/movies.csv")
data_genres = pd.read_csv("data/genres.csv")


genre_dict = dict(zip(data_genres["id"], data_genres["name"]))

def convert_genre_ids(genre_id_str):
    if isinstance(genre_id_str, str):
        genre_ids = ast.literal_eval(genre_id_str)
    else:
        genre_ids = genre_id_str

    return ",".join([genre_dict.get(genre_id, "Unknown") for genre_id in genre_ids])


data_movies["genres"] = data_movies["genre_ids"].apply(convert_genre_ids)

data_movies = data_movies.dropna()
data_movies.to_csv("data/movies_converted.csv", index=False)
