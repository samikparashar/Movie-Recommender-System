import pandas as pd
import streamlit as st
from streamlit import spinner
import zipfile
import pickle

movies_df = pickle.load(open('movies.pkl', 'rb'))
movies_list = movies_df['title'].values
movies = pd.DataFrame(movies_list)
# similarity = pickle.load(open('similarity.pkl', 'rb'))
with zipfile.ZipFile('similarity.pkl.zip', 'r') as zip_ref:
    with zip_ref.open('similarity.pkl') as file:
        similarity = pickle.load(file)
import requests

# st.write(movies_df)
API_KEY = "3eb4b919567514b6c509fb4e953f0c2e"


# def fetch_poster(movie_id):
#     if not movie_id:
#         return None
#     url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         data = response.json()
#         poster_path = data.get("poster_path")
#         if poster_path:
#             return "https://image.tmdb.org/t/p/w500" + poster_path
#         else:
#             return None
#     except requests.exceptions.RequestException:
#         return None
# def fetch_poster(movie_id, retries=3):
#     if not movie_id:
#         return None
#
#     url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
#
#     for _ in range(retries):
#         try:
#             response = requests.get(url, timeout=5)
#             response.raise_for_status()
#             data = response.json()
#
#             poster_path = data.get("poster_path")
#             if poster_path:
#                 return "https://image.tmdb.org/t/p/w500" + poster_path
#             else:
#                 return None
#
#         except requests.exceptions.RequestException:
#             continue  # try again
#
#     return None  # all retries failed
def fetch_poster(movie_id, retries=5):
    if not movie_id:
        return "https://via.placeholder.com/500x750?text=No+Poster"

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"

    for _ in range(retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            poster_path = data.get("poster_path")
            if poster_path:

                return "https://image.tmdb.org/t/p/w500" + poster_path

        except requests.exceptions.RequestException:
            continue


    try:
        backup_url = f"https://api.themoviedb.org/3/movie/{movie_id}/images?api_key={API_KEY}"
        r = requests.get(backup_url, timeout=5).json()
        if "posters" in r and len(r["posters"]) > 0:
            path = r["posters"][0]["file_path"]
            return "https://image.tmdb.org/t/p/w500" + path
    except:
        pass

    return "https://via.placeholder.com/500x750?text=No+Poster"


def recommend(movie):
    movie_index = movies_df[movies_df['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list1 = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies = []
    recommended_movies_poster = []
    for c in movies_list1:
        movie_id = movies_df.iloc[c[0]].get("id", None)
        recommended_movies.append(movies_df.iloc[c[0]].title)
        recommended_movies_poster.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_poster


st.title('Movie Recommender System')
selected_movie_name = st.selectbox(
    "How would you like to be contacted?",
    movies_list,
)

# if st.button("Recommend"):
#     names, posters = recommend(selected_movie_name)
if st.button("Recommend"):
    with st.spinner("Fetching recommendations..."):
        names, posters = recommend(selected_movie_name)

    cols = st.columns(5)

    for i, col in enumerate(cols):
        with col:
            st.text(names[i])
            if posters[i]:
                st.image(posters[i], use_container_width=True)
            else:
                st.write("No poster available")
