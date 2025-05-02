import os
from dotenv import load_dotenv
from fetch_movies import fetch_movies_data, fetch_genres

# Tải biến môi trường
load_dotenv()

# Lấy API_KEY từ biến môi trường
API_KEY = os.getenv("API_KEY")

# Path lưu dữ liệu
path_to_save = "./data"

def main():
    # Kiểm tra folder, nếu chưa tồn tại thì tạo mới
    if os.path.exists(path_to_save):
        pass
    else:
        os.makedirs(path_to_save)

    # Gọi hàm fetch_movies_data để lấy dữ liệu phim 
    fetch_movies_data(f"{path_to_save}/movies.csv", 500, 1, api_key=API_KEY)

    # Gọi hàm fetch_movies_data để lấy dữ liệu thể loại 
    fetch_genres("data/genres.csv", api_key=API_KEY)


if __name__ == "__main__":
    main()