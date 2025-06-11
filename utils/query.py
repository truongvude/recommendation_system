import sqlite3
import pandas as pd

def view_movies():
    conn = sqlite3.connect("movies_rating.db")
    query = "SELECT * FROM movies"
    movies_df = pd.read_sql_query(query, con=conn)
    print("\nDANH SÁCH PHIM")
    print(movies_df)
    conn.close()

def view_users():
    conn = sqlite3.connect("movies_rating.db")
    query = "SELECT * FROM users"
    users_df = pd.read_sql_query(query, con=conn)
    print("\nDANH SÁCH NGƯỜI DÙNG")
    print(users_df)
    conn.close()

def view_ratings():
    conn = sqlite3.connect('movies_rating.db')
    query = """
    SELECT 
        u.username,
        r.movie_id,
        m.title,
        r.rating,
        r.created_at
    FROM ratings r
    JOIN users u ON r.user_id = u.user_id
    JOIN movies m ON r.movie_id = m.id
    ORDER BY r.created_at DESC
    """
    ratings_df = pd.read_sql_query(query, conn)
    print("\nDANH SÁCH ĐÁNH GIÁ")
    print(ratings_df)
    conn.close()

def view_user_ratings(username):
    """Xem đánh giá của một người dùng cụ thể"""
    conn = sqlite3.connect('movies_rating.db')
    query = """
    SELECT 
        u.username,
        r.movie_id,
        m.title,
        r.rating,
        r.created_at
    FROM ratings r
    JOIN users u ON r.user_id = u.user_id
    JOIN movies m ON r.movie_id = m.id
    WHERE u.username = ?
    ORDER BY r.created_at DESC
    """
    ratings_df = pd.read_sql_query(query, conn, params=(username,))
    print(f"\nĐÁNH GIÁ CỦA NGƯỜI DÙNG {username}")
    print(ratings_df)
    conn.close()

def get_rating_stats():
    """Xem thống kê đánh giá"""
    conn = sqlite3.connect('movie_ratings.db')
    
    # Số lượng đánh giá theo người dùng
    query1 = """
    SELECT 
        u.username,
        COUNT(*) as total_ratings,
        AVG(r.rating) as avg_rating
    FROM ratings r
    JOIN users u ON r.user_id = u.user_id
    GROUP BY u.username
    """
    stats_df = pd.read_sql_query(query1, conn)
    print("\n=== THỐNG KÊ ĐÁNH GIÁ THEO NGƯỜI DÙNG ===")
    print(stats_df)
    
    # Phân bố điểm đánh giá
    query2 = """
    SELECT 
        rating,
        COUNT(*) as count
    FROM ratings
    GROUP BY rating
    ORDER BY rating
    """
    distribution_df = pd.read_sql_query(query2, conn)
    print("\n=== PHÂN BỐ ĐIỂM ĐÁNH GIÁ ===")
    print(distribution_df)
    
    conn.close()

def main():
    while True:
        print("\nCHỌN CHỨC NĂNG:")
        print("0. Xem danh sách phim")
        print("1. Xem danh sách người dùng")
        print("2. Xem tất cả đánh giá")
        print("3. Xem đánh giá của một người dùng")
        print("4. Xem thống kê đánh giá")
        print("0. Thoát")
        
        choice = input("Nhập lựa chọn của bạn: ")
        if choice == "0":
            view_movies()
        elif choice == "1":
            view_users()
        elif choice == "2":
            view_ratings()
        elif choice == "3":
            username = input("Nhập tên người dùng: ")
            view_user_ratings(username)
        elif choice == "4":
            get_rating_stats()
        elif choice == "0":
            break
        else:
            print("Lựa chọn không hợp lệ!") 
        
if __name__ == "__main__":
    main()