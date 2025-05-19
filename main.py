import os
import time
from dotenv import load_dotenv
import requests
import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle


# Load env
load_dotenv()

# Get API_KEY from environment variables
API_KEY = os.getenv("API_KEY")

# Path to saved
path_to_save = "./data"

def fetch_movies_data(path_to_save, end_page, start_page=1, api_key=None):
    """
    Fetch movies data from TMDB API \n
    :param path_to_save: location to save movies data
    :param end_page: last page to fetch data
    :param start_page: first page to get_data
    :api_key: credentials
    :return: fetched data is saved to path_to_save
    """
    for page in range(start_page, end_page+1):
        time.sleep(1)
        url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={api_key}&language=en-US&page={page}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            movies = [{"id": movies["id"],
                        "title": movies["title"],
                        "overview": movies["overview"],
                        "genre_ids": movies["genre_ids"],
                        "popularity": movies["popularity"],
                        "release_date": movies["release_date"],
                        "poster_path": movies["poster_path"],
                        "vote_average": movies["vote_average"],
                        "vote_count": movies["vote_count"]}
                        for movies in data.get("results", [])]
            
            df = pd.DataFrame(movies)
            header = page == 1
            df.to_csv(path_to_save, index=False, mode="a", header=header)
            print(f"Successfully fetched page {page}!")
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch page {page}: {e}")

def fetch_genres(path_to_save, language="en", api_key=None):
    """
    Fetch genres data from TMDB API \n
    :param path_to_save: location to save genres data
    :param language: language of genres (default: en)
    :api_key: credentials
    :return: fetched genres data is saved to path_to_save
    """
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}&language={language}"
    response = requests.get(url)
    data = response.json()
    genres = [{"id": genre["id"],
               "name": genre["name"]}
               for genre in data.get("genres", [])]
        
    df = pd.DataFrame(genres)
    df.to_csv(path_to_save, index=False)
    print("Successfully fetched genres data")


def convert_genre_ids(genre_id_str, genre_dict):
    if isinstance(genre_id_str, str):
        genre_ids = ast.literal_eval(genre_id_str)
    else:
        genre_ids = genre_id_str

    return ",".join([genre_dict.get(genre_id, "Unknown") for genre_id in genre_ids])

def transform(data_movies, data_genres):
    genre_dict = dict(zip(data_genres["id"], data_genres["name"]))
    data_movies["genres"] = data_movies["genre_ids"].apply(lambda genre_id_str: convert_genre_ids(genre_id_str, genre_dict))
    data_movies = data_movies.dropna()
    data_movies.loc[:, "tags"] = data_movies["overview"] + ' ' + data_movies["genres"]
    data_movies.to_csv("data/movies_transformed.csv")

    return data_movies

def main():
    # # Check folder, if not exists then create
    # if os.path.exists(path_to_save):
    #     pass
    # else:
    #     os.makedirs(path_to_save)

    # # Get movies data
    # fetch_movies_data(f"{path_to_save}/movies.csv", 500, 1, api_key=API_KEY)

    # # Get genres data
    # fetch_genres(f"{path_to_save}/genres.csv", api_key=API_KEY)

    data_movies = pd.read_csv("data/movies.csv")
    data_genres = pd.read_csv("data/genres.csv")

    data_movies_transformed = transform(data_movies, data_genres)

    cv = CountVectorizer(stop_words="english")
    vector = cv.fit_transform(data_movies_transformed["tags"].values.astype("U"))

    vector = vector.toarray()

    similarity = cosine_similarity(vector)

    similarity.dump(open("data/similarity.pkl", "wb"))
    pickle.dump(data_movies_transformed, open("data/movies_list.pkl", "wb"))

if __name__ == "__main__":
    main()