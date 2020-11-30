import requests
from bs4 import BeautifulSoup
import re
import csv
import json
from difflib import SequenceMatcher

with open("secrets/youtube_api.txt", "r") as f:
    youtube_key = f.read()
with open("secrets/omdb_api.txt", "r") as f:
    omdb_key = f.read()

class Episode:
    def __init__(self, season, episode):
        with open(f"pages/{season}-{episode}.html", "r") as f:
            self.html = f.read()
        self.season = season
        self.episode = episode
        # self.season, self.episode = re.search(r"season-(\d+)/episode-(\d+)", url).groups()
        self.soup = BeautifulSoup(self.html, "html.parser")
        self.youtube_id = self.soup.find("a", text="Youtube").get("href")[32:]
        self.airdate = self.soup.find("h5", text = "Original Air Date").parent.p.text
        hosts = self.soup.find("h5", text="Hosts / Guests").parent.find_all("div")
        self.hosts = "|".join([item.text for item in hosts])
        youtube_page = requests.get(f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={self.youtube_id}&key={youtube_key}")
        youtube_page_json = json.loads(youtube_page.content)
        youtube_statistics = youtube_page_json['items'][0]['statistics']
        self.view_count = youtube_statistics['viewCount']
        self.like_count = youtube_statistics['likeCount']
        self.dislike_count = youtube_statistics['dislikeCount']

    def get_classics(self):
        classics = self.soup.find("div", class_ = "classics")
        if not classics:
            return None
        self.classics = [Movie(soup) for soup in classics.find_all("div", recursive = False)]
        for movie in self.classics:
            movie.get_imdb()

    location_header = ",Latitude,Longitude,Quote,"
    def get_locations(self):
        location = self.soup.find("div", class_ = "locations")
        if not location:
            return None
        script = location.div.script.string
        self.location_quote = location.div.div.blockquote.text
        self.latitude, self.longitude = re.search(r"{lat: ([[\-\d\.]+), lng: ([\-\d\.]+)}", script).groups()
        self.location_movie = Movie(location)

    def review_rows(self):
        """The final csv output for movie reviews"""
        movies = self.soup.find("div", "episode-movies").find_all("div", recursive = False)
        self.movies = [Movie(soup) for soup in movies]
        for movie in self.movies:
            yield self.episode_csv() + movie.movie_csv() + movie.all_reviews_csv()
 
    def classics_rows(self):
        self.get_classics()
        try:
            for classic in self.classics:
                yield self.episode_csv() + classic.movie_csv()
        except AttributeError:
            pass
    
    def location_row(self):
        self.get_locations()
        try:
            return self.episode_csv() + [self.latitude, self.longitude, self.location_quote,
                                         self.location_movie.title, self.location_movie.year, self.location_movie.cover_url]
        except AttributeError:
            return self.episode_csv() + ["NA"] * 5
           
    header = "Season,Episode,Airdate,Hosts,Youtube_id,ViewCount,LikeCount,DislikeCount"
    def episode_csv(self):
        """Generic episode information regardless of segment"""
        return [self.season, self.episode, self.airdate, self.hosts,
                self.youtube_id, self.view_count, self.like_count, self.dislike_count]


class Movie:

    def __init__(self, soup):
        self.soup = soup
        self.title = soup.find("p", class_ = "movie-title").text
        self.year = re.match(r"\d+", soup.find(text="Year: ").next).group()
        # used to verify the omdb data
        self.website_plot = soup.find("p", class_ = "plot").text
        self.website_poster = soup.find("div", class_ = "movie-img").img.get("src")
        # convert for omdb
        if self.title == "Les Miserables":
            self.title = "Les Misérables"
        if self.title == "Escape from Planet Earth":
            self.year = 2012
        elif self.title == "Scary Movie 5":
            self.title = "Scary Movie V"
        elif self.title == "No Escape (aka The Coup)":
            self.title = "No Escape"
        elif self.title == "The Moon and the Sun":
            self.title = "The King's Daughter"
            self.year = 2020
        elif self.title == "Autobahn":
            self.title = "Collide"
        elif self.title == "The Last Full Measure":
            self.year = 2019
        elif self.title == "Fast & Furious 8":
            self.title = "The Fate of the Furious"

        # download data
        url = f"http://www.omdbapi.com/?t={self.title.replace('&', '%26')}&y={self.year}&apikey={omdb_key}"
        # if self.title == "21 & Over":
        #     url = f"http://www.omdbapi.com/?t=21+%26+Over&y=2013&apikey={omdb_key}"
        self.omdb = json.loads(requests.get(url).content)
        try:
            poster_id = re.compile(r"https://.*/images/M/([a-zA-Z0-9]+)")
            website_poster_id = poster_id.match(self.website_poster).group(1)
            omdb_poster_id = poster_id.match(self.omdb['Poster']).group(1)
            assert(website_poster_id == omdb_poster_id or (SequenceMatcher(None, self.website_plot, self.omdb['Plot']).ratio() > .90))
        except AssertionError:
            print("-" * 10)
            print(f"{self.title} ({self.year})")
            print(website_poster_id)
            print(omdb_poster_id)
            print(self.omdb['Plot'])
            print(self.website_plot)


    def __get_reviews__(self):
        reviews = self.soup.find("div", class_= "row reviews").find_all("div", class_ = "review-info")
        self.reviews = [Review(x.parent.parent) for x in reviews]
        self.reviews = [(review, review.author) for review in self.reviews]
        self.reviews_authors = [x[1] for x in self.reviews]


    def all_reviews_csv(self):
        self.__get_reviews__()
        authors = ['Gregg', 'Tim', 'John', 'Joe', 'Toni', 'Mark', 'Axiom', 'Ayaka', 'Larry']
        csv = []
        for author in authors:
            if author in self.reviews_authors:
                review = [review_pair[0] for review_pair in self.reviews if review_pair[1] == author][0]
                csv += [review.popcorn, review.oscar_pick]
            else:
                csv += ["NA"] * 2
        return csv


    header = ",Movie,Year,imdbID,Released,Rated,Genre,Director,Actors,imdbRating,imdbVotes"
    def movie_csv(self):
        return [self.title, self.year, self.omdb['imdbID'], self.omdb['Released'], self.omdb['Rated'],
                self.omdb['Genre'], self.omdb['Director'], self.omdb['Actors'],
                self.omdb['imdbRating'], self.omdb['imdbVotes']]
        
    def __repr__(self):
        return f"{self.title} ({self.year})"

    
class Review:
    authors = ['Gregg', 'Tim', 'John', 'Joe', 'Toni', 'Mark', 'Axiom', 'Ayaka', 'Larry']
    header = "," + ",".join([x + "_popcorn" + "," + x + "_oscar" for x in authors])

    def __init__(self, soup):
        author_full = soup.find("p", class_ = "title").text
        self.author = re.match(r"(\w+)'s Review", author_full).group(1)
        if soup.find("p", class_ = "did-not-rate"):
            self.popcorn = "NA"
        else:
            review_text = soup.find("p", class_ = "rating-summary").text
            popcorn = re.match(r"\d+", review_text)
            self.popcorn = popcorn.group(0)
        self.oscar_pick = bool(soup.find("div", class_ = "oscar-badge"))
    

