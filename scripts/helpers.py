import json
import requests
import pathlib

PROJECT_ROOT = str(pathlib.Path(__file__).parent.parent)

with open(PROJECT_ROOT + "/secrets/omdb_api.txt", "r") as f:
    omdb_key = f.read()

with open(PROJECT_ROOT + "/secrets/youtube_api.txt", "r") as f:
    youtube_key = f.read()

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

def get_omdb_data(title, year):
    omdb = json.loads(requests.get(omdb_url(title, year)).content)
    omdb.pop('Ratings', None) # superfluous, and removing makes it easier to join data
    return omdb