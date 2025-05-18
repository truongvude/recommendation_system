import os
from dotenv import load_dotenv
from fetch_movies import fetch_movies_data, fetch_genres

# Load env
load_dotenv()

# Get API_KEY from environment variables
API_KEY = os.getenv("API_KEY")

# Path to saved
path_to_save = "./data"

def main():
    # Check folder, if not exists then create
    if os.path.exists(path_to_save):
        pass
    else:
        os.makedirs(path_to_save)

    # Get movies data
    fetch_movies_data(f"{path_to_save}/movies.csv", 500, 1, api_key=API_KEY)

    # Get genres data
    fetch_genres("data/genres.csv", api_key=API_KEY)


if __name__ == "__main__":
    main()