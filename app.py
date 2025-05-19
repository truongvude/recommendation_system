import os
from dotenv import load_dotenv
import streamlit as st
import pickle

movies = pickle.load(open("data/movies_list.pkl", "rb"))
similarity = pickle.load(open("data/similarity.pkl", "rb"))
movies_list = movies["title"]

# Load environment variable
load_dotenv()
API_KEY = os.getenv("API_KEY")

def recommend(movie):
    """
    Suggest movies similar to the selected movie \n
    :param movie: movie need similar recommendations
    :return: list of recommended movies and information
    """
    index=movies[movies['title']==movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector:vector[1])
    recommendations = []
    for i in distance[1:6]:  # Top 5 recommendations
        movie_data = movies.iloc[i[0]]
        recommendations.append({
            "title": movie_data.title,
            "poster": f"https://image.tmdb.org/t/p/w500{movie_data.poster_path}",
            "overview": movie_data.overview,
            "genres": movie_data.genres,
            "release_date": movie_data.release_date,
            "vote_average": movie_data.vote_average,
            "vote_count": movie_data.vote_count
        })

    return recommendations


def main():
    st.header("Movie Recommender System")

    selectvalue=st.selectbox("Select movie from dropdown", movies_list)
    if st.button("Show Recommend"):
        recommendations = recommend(selectvalue)
        for movie in recommendations:
            with st.container():
                st.markdown(f"**{movie['title']}**")
                st.image(movie["poster"])
                with st.expander("Movie information"):
                    st.markdown(f"**Overview:** {movie['overview']}")
                    st.markdown(f"**Genres:** {movie['genres']}")
                    st.markdown(f"**Release date:** {movie['release_date']}")
                    st.markdown(f"**Vote average:** {movie['vote_average']}")
                    st.markdown(f"**Vote count:** {movie['vote_count']}")
                
if __name__ == "__main__":
    main()