import streamlit as st
import pickle
import requests

# Load movies list and similarity matrix from pickle files
try:
    movies = pickle.load(open("movies_list.plk", 'rb'))
    similarity = pickle.load(open("similarity.plk", 'rb'))
except FileNotFoundError as e:
    st.error(f"File not found: {e}")
    st.stop()

# Extract movie titles
movies_list = movies['title'].values

# Streamlit header
st.header('Movie Recommendation System')

# Dropdown for movie selection
selectvalue = st.selectbox('Select movies from Dropdown', movies_list)

# Fetch movie poster from API
def fetch_poster(movie_id):
    api_key = "ba67e38b06b28bf2ee486d4f881bbfee"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        poster_path = data.get('poster_path', '')
        if poster_path:
            full_path = f"https://image.tmdb.org/t/p/w500{poster_path}"
            return full_path
    st.warning(f"Failed to fetch poster for movie ID {movie_id}. Status code: {response.status_code}")
    return None

# Function to recommend movies
def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), key=lambda vector: vector[1], reverse=True)
        recommended_movies = []
        recommended_posters = []
        for i in distances[1:6]:  # Starting from 1 to avoid the movie itself
            movie_id = movies.iloc[i[0]].id
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_posters.append(fetch_poster(movie_id))
        return recommended_movies, recommended_posters
    except Exception as e:
        st.error(f"An error occurred in recommendation function: {e}")
        return [], []

# Button to show recommendations
if st.button("Show Recommend"):
    try:
        movie_names, movie_posters = recommend(selectvalue)
        if not movie_names:
            st.warning("No recommendations found.")
        cols = st.columns(5)
        for col, movie_name, movie_poster in zip(cols, movie_names, movie_posters):
            with col:
                st.text(movie_name)
                if movie_poster:
                    st.image(movie_poster)
                else:
                    st.text("Poster not available")
    except Exception as e:
        st.error(f"An error occurred while fetching recommendations: {e}")
