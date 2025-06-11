# Import thư viện
import sqlite3
import pandas as pd
from datetime import datetime

def init_db():
    """
    Khởi tạo 3 bảng movies, users và ratings
    """
    conn = sqlite3.connect("movies_rating.db")
    cursor = conn.cursor()
    movies_df = pd.read_csv("data/movies.csv")

    # Tạo bảng movies
    try:
        movies_df.loc[:, ["id", "title"]].to_sql("movies", con=conn, index=False)
    except ValueError as e:
        if 'already exists' in str(e):
            print("Bảng đã được tạo trước đó, bỏ qua.")
        else:
            raise 

    # Tạo bảng users
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                   )
                   """)
    
    # Tạo bảng ratings
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS ratings (
                        rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        movie_id INTEGER,
                        rating FLOAT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id),
                        FOREIGN KEY (movie_id) REFERENCES movies (id),
                        UNIQUE(user_id, movie_id)
                   )
                   """)
  
    # Commit và đóng kết nối
    conn.commit()
    conn.close()


def add_user(username):
    """
    Tạo mới user trong CSDL. Nếu đã tồn tại người dùng thì trả về user_id tương ứng.\n
    :param username: Tên user cần tạo
    :return user_id: Id của user vừa tạo 
    """
    try:
        conn = sqlite3.connect("movies_rating.db")
        cursor = conn.cursor()
        # Tạo user mới
        cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()
        user_id = cursor.lastrowid

    # Nếu đã username đã tồn tại thì tìm id hiện tại 
    except sqlite3.IntegrityError:
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (username, ))
        user_id = cursor.fetchone()[0]

    # Đóng kết nối
    finally:
        conn.close()

    return user_id

def add_rating(user_id, movie_id, rating):
    """
    Thêm đánh giá của người dùng cho phim.\n
    :param user_id: ID của người đánh giá
    :param movie_id: ID của phim cần đánh giá
    :param rating: Số điểm đánh giá
    """
    conn = sqlite3.connect("movies_rating.db")
    cursor = conn.cursor()
    created_at = datetime.now()

    try:
        if isinstance(movie_id, bytes):
            movie_id = int.from_bytes(movie_id, byteorder="little")
        else:
            movie_id = int(movie_id)
    
        cursor.execute("""INSERT INTO ratings (user_id, movie_id, rating, created_at)
                   VALUES (?, ?, ?, ?)
                   """, (user_id, movie_id, rating, created_at))

        conn.commit()
    
    finally:
        conn.close()
    

def get_user_rating(user_id):
    """
    Truy vấn các đánh giá của người dùng cụ thể\n
    :param user_id: ID của người dùng cần xem
    :return df: dataframe danh sách các lượt đánh giá của người dùng dựa trên id của họ
    """
    conn = sqlite3.connect("movies_rating.db")

    query = "SELECT movie_id, rating FROM ratings WHERE user_id = ?"

    df = pd.read_sql_query(query, con=conn, params=(user_id,))
    conn.close()

    if df.shape[0] > 0 and isinstance(df["movie_id".iloc[0], bytes]):
        df["movie_id"] = df["movie_id"].apply(lambda x: int.from_bytes(x, byteorder="little"))
    return df

def get_all_ratings():
    """
    Truy vấn tất cả các đánh giá\n
    :return df: dataframe danh sách các lượt đánh giá của tất cả người dùng
    """
    conn = sqlite3.connect("movies_rating.db")

    query = "SELECT user_id, movie_id, rating FROM ratings"
    
    df = pd.read_sql_query(query, conn)

    conn.close()

    if df.shape[0] > 0 and isinstance(df['movie_id'].iloc[0], bytes):
        df['movie_id'] = df['movie_id'].apply(lambda x: int.from_bytes(x, byteorder='little'))
    
    return df

def drop_table(table_name):
    """
    Xóa bảng \n
    :param table_name: tên bảng
    """
    conn = sqlite3.connect("movies_rating.db")
    cursor = conn.cursor()

    cursor.execute(f"DROP TABLE {table_name}")

    conn.commit()
    print(f"Xóa thành công bảng {table_name}")
    conn.close()

# Khởi tạo bảng
init_db()