import os
import streamlit as st
import pickle
import requests
from utils.database import add_user, add_rating, get_all_ratings
from utils.collaborative_filter import create_user_movie_matrix, get_collaborative_recommendations, get_user_recommendations
from dotenv import load_dotenv

# Load API_KEY của IMDB
load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

@st.cache_data(ttl=3600)
def fetch_poster(movie_id):
    """
    Trả về đường dẫn tới ảnh dựa trên ID phim.\n
    :params movie_id: ID của phim
    :return full_path: Đường link tới ảnh.
    """
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        data = requests.get(url)
        data = data.json()
        poster_path = data['poster_path']
        full_path = "https://image.tmdb.org/t/p/w500/"+poster_path
        return full_path
    except:
        return None

@st.cache_data(ttl=3600)
def get_movie_info(movie_id):
    """
    Trả về thông tin của phim dựa trên ID.\n
    :params movie_id: ID của phim
    :return movie_info: Dataframe chứa thông tin của phim.
    """
    try:
        movie_info = movies[movies['id'] == movie_id].iloc[0]
        return movie_info
    except:
        return None

@st.cache_data(ttl=3600)
def load_movie_data():
    """
    Tải dữ liệu phim từ file pickle.\n
    :return movies: Dataframe chứa thông tin phim
    :return similarity: Ma trận thể hiện mức độ tương đồng giữa các bộ phim.
    """
    movies = pickle.load(open("data/movies_list.pkl", 'rb'))
    similarity = pickle.load(open("data/similarity.pkl", 'rb'))
    return movies, similarity

@st.cache_data(ttl=60)  # Lưu bộ nhớ đệm 1 phút 
def get_popular_posters():
    """
    Lấy đường dẫn ảnh của một số phim phổ biến\n
    :return poster: Mảng chứa đường link tới ảnh của các phim.
    """
    movie_ids = [176983, 372058, 176, 2830, 429422, 475557]
    posters = []
    for movie_id in movie_ids:
        poster = fetch_poster(movie_id)
        if poster:
            posters.append(poster)
    return posters

def display_movie_recommendations(movie_ids):
    """
    Hiển thị gợi ý phim\n
    :param movie_ids: Mảng chứa các bộ phim được gợi ý
    :return: Hiển thị ảnh và tiêu đề của phim.
    """
    valid_recommendations = []
    for movie_id in movie_ids:
        movie_info = get_movie_info(movie_id)
        poster = fetch_poster(movie_id)
        if movie_info is not None and poster is not None:
            valid_recommendations.append((movie_info.title, poster))
        if len(valid_recommendations) >= 5:
            break
    
    if valid_recommendations:
        cols = st.columns(len(valid_recommendations))
        for i, (title, poster) in enumerate(valid_recommendations):
            with cols[i]:
                st.text(title)
                st.image(poster)
    else:
        st.warning("Không thể tải thông tin phim. Vui lòng thử lại sau.")

# Tải dữ liệu phim 
movies, similarity = load_movie_data()
movies_list = movies['title'].values

# Khởi tạo session
if 'current_movie' not in st.session_state:
    st.session_state.current_movie = None
if 'current_rating' not in st.session_state:
    st.session_state.current_rating = 3.0
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Đăng nhập
if st.session_state.user_id is None:
    st.title("Chào mừng tới hệ thống gợi ý phim!")
    username = st.text_input("Nhập vào tên người dùng")
    if st.button("Đăng nhập"):
        if username:
            user_id = add_user(username)
            st.session_state.user_id = user_id
            st.session_state.username = username  # Lưu lại username
            st.success(f"Xin chào, {username}!")
            st.rerun()
else:
    st.header("Hệ thống gợi ý phim")
    st.subheader(f"Xin chào, {st.session_state.username}!")
    st.subheader("Một số phim nổi bật")
    posters = get_popular_posters()
    if posters:
        cols = st.columns(len(posters))
        for i, poster_url in enumerate(posters):
            with cols[i]:
                st.image(poster_url, use_container_width=True)
    else:
        st.warning("Không thể tải poster phim để hiển thị.")
    # Thêm mục đánh giá phim
    st.subheader("Đánh giá phim")
    rate_movie = st.selectbox("Chọn phim cần đánh giá", movies_list, key='rate_movie')
    if rate_movie != st.session_state.current_movie:
        st.session_state.current_movie = rate_movie
        st.session_state.current_rating = 3.0
    
    rating = st.slider("Đánh giá phim này theo thang điêm 1-5:", 1.0, 5.0, st.session_state.current_rating, 0.5)
    if rating != st.session_state.current_rating:
        st.session_state.current_rating = rating
    
    if st.button("Đánh giá"):
        try:
            movie_idx = movies[movies['title'] == rate_movie].index[0]
            movie_id = movies.iloc[movie_idx].id
            add_rating(st.session_state.user_id, movie_id, rating)
            st.success("Đánh giá thành công!")
        except Exception as e:
            st.error(f"Lỗi khi đánh giá: {str(e)}")

    # Mục gợi ý phim 
    st.subheader("Nhận Gợi Ý Phim")
    rec_method = st.radio(
        "Chọn phương pháp gợi ý:",
        ["Dựa trên nội dung", "Dựa trên phim", "Dựa trên người dùng", "Kết hợp"]
    )
    
    if rec_method == "Dựa trên người dùng":
        if st.button("Xem gợi ý cho tôi"):
            ratings_df = get_all_ratings()
            if not ratings_df.empty and len(ratings_df['user_id'].unique()) > 1:
                movie_ids = get_user_recommendations(st.session_state.user_id, ratings_df)
                if movie_ids:
                    st.success("Dựa trên lịch sử đánh giá của bạn, đây là những phim bạn có thể thích:")
                    display_movie_recommendations(movie_ids)
                else:
                    st.warning("Không thể đưa ra gợi ý. Hãy đánh giá thêm phim!")
            else:
                st.warning("Cần thêm dữ liệu đánh giá từ nhiều người dùng để sử dụng tính năng này.")
    else:
        selectvalue = st.selectbox("Chọn một bộ phim:", movies_list, key='recommend_movie')
        
        if st.button("Xem gợi ý"):
            try:
                movie_idx = movies[movies['title'] == selectvalue].index[0]
                movie_id = movies.iloc[movie_idx].id
                
                if rec_method == "Dựa trên nội dung":
                    # Gợi ý dựa trên nội dung
                    distance = sorted(list(enumerate(similarity[movie_idx])), reverse=True, key=lambda vector:vector[1])
                    movie_ids = [movies.iloc[i[0]].id for i in distance[1:6]]
                elif rec_method == "Dựa trên phim":
                    # Gợi ý dựa trên phim
                    ratings_df = get_all_ratings()
                    if not ratings_df.empty:
                        user_movie_matrix = create_user_movie_matrix(ratings_df)
                        movie_ids = get_collaborative_recommendations(movie_id, user_movie_matrix)
                    else:
                        st.warning("Không đủ dữ liệu đánh giá. Sử dụng phương pháp dựa trên nội dung.")
                        distance = sorted(list(enumerate(similarity[movie_idx])), reverse=True, key=lambda vector:vector[1])
                        movie_ids = [movies.iloc[i[0]].id for i in distance[1:6]]
                else:  # Gợi ý kết hợp
                    # Kết hợp hai phương pháp
                    content_based = [movies.iloc[i[0]].id for i in sorted(list(enumerate(similarity[movie_idx])), reverse=True, key=lambda vector:vector[1])[1:6]]
                    collaborative = []
                    ratings_df = get_all_ratings()
                    if not ratings_df.empty:
                        user_movie_matrix = create_user_movie_matrix(ratings_df)
                        collaborative = get_collaborative_recommendations(movie_id, user_movie_matrix)
                    
                    # Gộp hai cách gợi ý riêng biệt
                    movie_ids = []
                    seen = set()
                    for mid in content_based + collaborative:
                        if mid not in seen and len(movie_ids) < 5:
                            movie_ids.append(mid)
                            seen.add(mid)
                
                if movie_ids:
                    display_movie_recommendations(movie_ids)
                else:
                    st.warning("Không thể tìm thấy gợi ý phù hợp.")
            except Exception as e:
                st.error(f"Lỗi gợi ý: {str(e)}")

    # Đăng xuất
    if st.button("Đăng xuất"):
        st.session_state.user_id = None
        st.rerun()
