from sklearn.metrics.pairwise import cosine_similarity

def create_user_movie_matrix(ratings_df):
    """
    Tạo ma trận tiện ích (utility matrix) giữa người dùng và các bộ phim đã được đánh giá.\n
    :params ratings_df: DataFrame chứa dữ liệu đánh giá của người dùng với các cột: 'user_id', 'movie_id', 'rating'.
    :return user_movie_matrix: Ma trận tiện ích với các hàng là người dùng, cột là phim và giá trị là điểm đánh giá.
    Trả về None nếu dữ liệu đầu vào rỗng.
    """
    if ratings_df is None or ratings_df.empty:
        return None
    
    # Tạo ma trận tiện ích giữa người dùng và phim
    user_movie_matrix = ratings_df.pivot_table(
        index='user_id',
        columns='movie_id',
        values='rating'
    ).fillna(0)
    
    return user_movie_matrix

def get_collaborative_recommendations(movie_id, user_movie_matrix, n_recommendations=5):
    """
    Gợi ý dựa trên một bộ phim cụ thể (item-based collaborative filtering)\n
    :param movie_id: ID bộ phim cần gợi ý
    :param user_movie_matrix: Ma trận tiện ích giữa người dùng và các bộ phim được đánh giá
    :param n_recommendations: Số bộ phim gợi ý. Mặc định là 5.
    :return recommendations: Mảng chứa các bộ phim được gợi ý"""
    if user_movie_matrix is None:
        return []
        
    # Tính ma trận tương đồng giữa các bộ phim
    movie_similarity = cosine_similarity(user_movie_matrix.T)
        
    # Lấy index của phim
    try:
        movie_idx = user_movie_matrix.columns.get_loc(movie_id)
    except:
        return []
    
    # Tìm các bộ phim giống nhau
    similar_scores = movie_similarity[movie_idx]
    similar_movies = list(enumerate(similar_scores))
    similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)
    
    # Lấy top N gợi ý (trừ phim đã chọn)
    recommendations = []
    for i in similar_movies[1:n_recommendations+1]:
        recommendations.append(user_movie_matrix.columns[i[0]])
    
    return recommendations

def get_user_recommendations(user_id, ratings_df, n_recommendations=5):
    """Gợi ý dựa trên lịch sử đánh giá của người dùng (user-based collaborative filtering)\n
    :param user_id: ID của người dùng cần gợi ý
    :param ratings_df: DataFrame chứa dữ liệu đánh giá của người dùng với các cột: 'user_id', 'movie_id', 'rating'.
    :param n_recommendations: Số bộ phim gợi ý. Mặc định là 5.
    :return recommendations: Mảng chứa các bộ phim được gợi ý
    """
    if ratings_df is None or ratings_df.empty:
        return []

    # Tạo ma trận user-movie
    user_movie_matrix = create_user_movie_matrix(ratings_df)
    if user_movie_matrix is None:
        return []

    # Tính toán độ tương đồng giữa các người dùng
    user_similarity = cosine_similarity(user_movie_matrix)
    
    try:
        # Lấy index của user hiện tại
        user_idx = user_movie_matrix.index.get_loc(user_id)
    except:
        return []

    # Lấy điểm số tương đồng với các user khác
    similar_scores = user_similarity[user_idx]
    similar_users = list(enumerate(similar_scores))
    similar_users = sorted(similar_users, key=lambda x: x[1], reverse=True)

    # Lọc ra các phim mà user hiện tại chưa đánh giá
    user_ratings = user_movie_matrix.iloc[user_idx]
    unwatched_movies = user_ratings[user_ratings == 0].index

    # Tính điểm dự đoán cho các phim chưa xem
    movie_scores = {}
    for movie_id in unwatched_movies:
        movie_ratings = user_movie_matrix[movie_id]
        weighted_sum = 0
        similarity_sum = 0

        # Tính điểm dự đoán dựa trên đánh giá của các user tương đồng
        for i, sim_score in similar_users[1:]:  # Bỏ qua user hiện tại
            if movie_ratings.iloc[i] > 0:  # Chỉ xét các user đã đánh giá phim này
                weighted_sum += sim_score * movie_ratings.iloc[i]
                similarity_sum += sim_score

        if similarity_sum > 0:
            movie_scores[movie_id] = weighted_sum / similarity_sum

    # Sắp xếp và lấy top N phim có điểm cao nhất
    sorted_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)
    recommendations = [movie_id for movie_id, score in sorted_movies[:n_recommendations]]

    return recommendations 