import pathlib
from bs4 import BeautifulSoup
import re
from helpers import get_omdb_data, PROJECT_ROOT
from functools import reduce
import pandas as pd


def review_info(soup):
    review = {}
    author_full = soup.find("p", class_ = "title").text
    review['author'] = re.match(r"(\w+)'s Review", author_full).group(1)
    if soup.find("p", class_ = "did-not-rate"):
        review["popcorn"] = "NA"
    else:
        review_text = soup.find("p", class_ = "rating-summary").text
        popcorn = re.match(r"\d+", review_text)
        review["popcorn"] = popcorn.group(0)
    review["oscar_pick"] = bool(soup.find("div", class_ = "oscar-badge"))
    return review

def movie_info(soup):
    """Returns all movie data, including reviews for one movie as list with item per review"""
    title = soup.find("p", class_ = "movie-title").text
    year = re.match(r"\d+", soup.find(text="Year: ").next).group()
    omdb = get_omdb_data(title, year)
    reviews_soup = soup.find("div", class_= "row reviews").find_all("div", class_ = "review-info")
    reviews = [review_info(soup) for soup in reviews_soup]
    movie_data = [omdb | review for review in reviews]
    return movie_data

def get_all_movie_info(season, episode_number):
    """Returns list of all movie info"""
    path = PROJECT_ROOT + f"/pages/{season}-{episode_number}.html"
    with open(path, "r") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    movies_soup = soup.find("div", "episode-movies").find_all("div", recursive = False)
    movies = [movie_info(soup) for soup in movies_soup]
    movies_flattened = reduce(lambda x, y: x + y, movies) # grab all review rows from lists
    movies_complete = [{"season": season, "episode": episode_number} | data for data in movies_flattened]

    return movies_complete

reviews = []
for season in range(1, 12):
        for episode_number in range(1, 11):
            print(f"Parsing movie reviews for {season}-{episode_number}")
            reviews += get_all_movie_info(season, episode_number)
reviews_df = pd.DataFrame(reviews)
reviews_df.to_csv(PROJECT_ROOT + "/datasets/movie_info.csv", index = False)