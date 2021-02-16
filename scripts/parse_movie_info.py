import pathlib
from bs4 import BeautifulSoup
import re
import json
import requests
from functools import reduce
import pandas as pd

with open(str(pathlib.Path(__file__).parent.parent) + "/secrets/omdb_api.txt", "r") as f:
    omdb_key = f.read()

def omdb_url(title, year):
    """From the title and year get the url for omdb"""
    # adjust data to match omdb
    if title == "CafÃ© Society":
        title = "Café Society"
    if title == "Les Miserables":
        title = "Les Misérables"
    if title == "Escape from Planet Earth":
        year = 2012
    elif title == "Scary Movie 5":
        title = "Scary Movie V"
    elif title == "No Escape (aka The Coup)":
        title = "No Escape"
    elif title == "The Moon and the Sun":
        title = "The King's Daughter"
        year = 2020
    elif title == "Autobahn":
        title = "Collide"
    elif title == "The Last Full Measure":
        year = 2019
    elif title == "Fast & Furious 8":
        title = "The Fate of the Furious"

    url = f"http://www.omdbapi.com/?t={title.replace('&', '%26')}&y={year}&apikey={omdb_key}"
    return url

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
    omdb = json.loads(requests.get(omdb_url(title, year)).content)
    omdb.pop('Ratings', None) # make it easier to join data

    reviews_soup = soup.find("div", class_= "row reviews").find_all("div", class_ = "review-info")
    reviews = [review_info(soup) for soup in reviews_soup]
    movie_data = [omdb | review for review in reviews]
    return movie_data

def get_all_movie_info(season, episode_number):
    """Returns list of all movie info"""
    root_path = pathlib.Path(__file__).parent.parent
    path = str(root_path) + f"/pages/{season}-{episode_number}.html"
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
reviews_df.to_csv(str(pathlib.Path(__file__).parent.parent) + "/datasets/movie_info.csv", index = False)