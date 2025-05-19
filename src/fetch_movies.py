import pandas as pd
import requests
import time

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