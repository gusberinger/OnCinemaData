import glob
from bs4 import BeautifulSoup
import requests
import json
import re
import pandas as pd
from functools import reduce

with open("secrets/youtube_api.txt", "r") as f:
    youtube_key = f.read()


def epsiode_info(season, episode_number):
    """Returns as a list of dictionaries all relevent information considering movies
    and reviews of those movies in the episode."""
    with open(f"pages/{season}-{episode_number}.html", "r") as f:
        html = f.read()

    episode = {"season": season, "episode": episode_number}
    soup = BeautifulSoup(html, "html.parser")
    episode["youtube_id"] = soup.find("a", text="Youtube").get("href")[32:]
    episode["airdate"] = soup.find("h5", text = "Original Air Date").parent.p.text
    hosts = soup.find("h5", text="Hosts / Guests").parent.find_all("div")
    episode["hosts"] = "|".join([item.text for item in hosts])
    episode["n_hosts"] = len(hosts)
    youtube_api_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={episode['youtube_id']}&key={youtube_key}"
    youtube_data_all = json.loads(requests.get(youtube_api_url).content)
    youtube_data = youtube_data_all['items'][0]['statistics']
    
    complete_data = episode | youtube_data
    print(complete_data)
    return complete_data


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

def get_all_movie_info(season, episode_numer):
    """Returns list of all movie info"""
    with open(f"pages/{season}-{episode_number}.html", "r") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    movies_soup = soup.find("div", "episode-movies").find_all("div", recursive = False)
    movie_data = {"season": season, "episode": episode_number}
    movies = [movie_info(soup) for soup in movies_soup]
    movies_flattened = reduce(lambda x, y: x + y, movies) # grab all review rows from lists
    print(movies_flattened)


all_episode_info = []
for season in range(1, 12):
    for episode_number in range(1, 11):
        print(f"Parsing {season}-{episode_number}")
        get_all_movie_info(season, episode_number)
        all_episode_info.append(epsiode_info(season, episode_number))
df = pd.DataFrame(all_episode_info)
df.to_csv("datasets/episode_info.csv", index = False)