import glob
from bs4 import BeautifulSoup
import requests
import json
import re
import pandas as pd
from functools import reduce

with open("secrets/youtube_api.txt", "r") as f:
    youtube_key = f.read()
with open("secrets/omdb_api.txt", "r") as f:
    omdb_key = f.read()

def epsiode_info(season, episode_number):
    """Returns as a list of dictionaries all relevent information considering movies
    and reviews of those movies in the episode."""
    with open(f"pages/{season}-{episode_number}.html", "r") as f:
        html = f.read()

    episode = {}
    episode["season"] = season
    episode["episode"] = episode_number
    soup = BeautifulSoup(html, "html.parser")
    episode["youtube_id"] = soup.find("a", text="Youtube").get("href")[32:]
    episode["airdate"] = soup.find("h5", text = "Original Air Date").parent.p.text
    hosts = soup.find("h5", text="Hosts / Guests").parent.find_all("div")
    episode["hosts"] = "|".join([item.text for item in hosts])
    youtube_api_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={episode['youtube_id']}&key={youtube_key}"
    youtube_data_all = json.loads(requests.get(youtube_api_url).content)
    youtube_data = youtube_data_all['items'][0]['statistics']
    movies_soup = soup.find("div", "episode-movies").find_all("div", recursive = False)
    movies = [movie_info(soup) for soup in movies_soup]
    movies_flattened = reduce(lambda x, y: x + y, movies) # grab all review rows from lists
    complete_data = [episode | movie for movie in movies_flattened]
    return complete_data

def omdb_url(title, year):
    """From the title and year get the url for omdb"""
    # adjust data to match omdb
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


if __name__ == "__main__":
    all_episode_info = []
    for season in range(1, 12):
        for episode_number in range(1, 11):
            print(f"Parsing {season}-{episode_number}")
            for row in epsiode_info(season, episode_number):
                all_episode_info.append(row)
    df = pd.DataFrame(all_episode_info)
    df.to_csv("datasets/movie_reviews.csv", index = False)