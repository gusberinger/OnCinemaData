import glob
from bs4 import BeautifulSoup
import requests
import json
import re
import pandas as pd
from functools import reduce
import pathlib

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
    return complete_data

all_episode_info = []
for season in range(1, 12):
    for episode_number in range(1, 11):
        print(f"Parsing {season}-{episode_number}")
        all_episode_info.append(epsiode_info(season, episode_number))

episode_df = pd.DataFrame(all_episode_info)
episode_df.to_csv(str(pathlib.Path(__file__).parent.parent) + "/datasets/episode_info.csv", index = False)