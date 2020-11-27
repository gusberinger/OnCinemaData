import requests
from bs4 import BeautifulSoup
import re
import csv
from imdb import IMDb
import json
from difflib import SequenceMatcher

with open("api.txt", "r") as f:
    api_key = f.read()

ia = IMDb()

# fill in data from oncinematimeline that does not match imdb
imdb_na = {"Escape from Planet Earth": "0765446",
           "Scary Movie 5": "0795461",
           "Star Trek: Beyond": "2660888",
           "Sin City: A Dame to Kill For": "0458481",
           "No Escape (aka The Coup)": "1781922",
           "The Moon and the Sun": "2328678",
           "Star Trek Beyond": "2660888",
           "Fast & Furious 8": "4630562",
           "Acrimony": "6063050",
           "Insurgent": "2908446"}

winners = []
with open("oscar.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        title, year, imdb_id = row
        winners.append(imdb_id)

class Episode:
    def __init__(self, url):
        self.html = requests.get(url).text
        self.season, self.episode = re.search(r"season-(\d+)/episode-(\d+)", url).groups()
        self.soup = BeautifulSoup(self.html, "html.parser")
        self.youtube_id = self.soup.find("a", text="Youtube").get("href")[32:]
        self.airdate = self.soup.find("h5", text = "Original Air Date").parent.p.text
        hosts = self.soup.find("h5", text="Hosts / Guests").parent.find_all("div")
        self.hosts = "|".join([item.text for item in hosts])
        movies = self.soup.find("div", "episode-movies").find_all("div", recursive = False)
        self.movies = [Movie(soup) for soup in movies]
        for movie in self.movies:
            movie.get_imdb()

    def get_youtube(self):
        page = requests.get(f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={self.youtube_id}&key={api_key}")
        page_json = json.loads(page.content)
        statistics = page_json['items'][0]['statistics']
        self.view_count = statistics['viewCount']
        self.like_count = statistics['likeCount']
        self.dislike_count = statistics['dislikeCount']

    def write_csv(self, file_name):
        with open(file_name, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for movie in self.movies:
                row = [self.season, self.episode, self.airdate, self.hosts,
                       self.youtube_id, self.view_count, self.like_count, self.dislike_count] + movie.csv()
                writer.writerow(row)

class Movie:
    def __init__(self, soup):
        self.soup = soup
        self.title = soup.find("p", class_ = "movie-title").text
        self.year = re.match(r"\d+", self.soup.find(text="Year: ").next).group()
        self.description = soup.find("p", class_ = "plot").text
        
        self.reviews = {}
        reviews_soup = soup.find("div", class_= "row reviews").find_all("div", class_ = "review-info")
        # go up two levels to get oscar information
        reviews_soup = [x.parent.parent for x in reviews_soup]

        for review in reviews_soup:
            author = review.find("p", class_ = "title").text
            author = re.match(r"(\w+)'s Review", author).group(1)
            self.reviews[author] = self.build_review_db(review)


    def get_imdb(self):
        # not all data on website matches imdb
        if self.title in imdb_na.keys():
            self.imdb_id = imdb_na[self.title]
            imdb_movie = ia.get_movie(self.imdb_id)
        else:
            imdb_movie = ia.search_movie(f"{self.title} ({self.year})")[0]

        self.imdb_id = imdb_movie.getID()
        self.oscar_winner = self.imdb_id in winners
        ia.update(imdb_movie)
        try:
            self.imdb_rating = imdb_movie['rating']
            self.runtime = imdb_movie['runtime'][0]
            self.imdb_votes = imdb_movie['votes']
            self.imdb_cast = "|".join([x['name'] for x in imdb_movie['cast']][:5])
        except KeyError:
            self.imdb_rating = "NA"
            self.runtime = "NA"
            self.imdb_votes = "NA"
            self.imdb_cast = "NA"

        # make sure that the movies line up
        try:
            plot = imdb_movie['plot'][0]
            if "::" in plot:
                plot = re.match(r"(.*)::", plot).group(1)
            assert(SequenceMatcher(None, plot, self.description).ratio() > .90)
        except AssertionError:
            print("-" * 10)
            print(plot)
            print(self.description)
            print(self.title)
            print(self.year)
            print(f"http://imdb.com/title/tt{self.imdb_id}")


    def build_review_db(self, review):
        """Build a database of information for each review"""
        db = {}
        # the rating does not necessarily exist
        try:
            review_text = review.find("p", class_ = "rating-summary").text
            db['popcorn'] = re.match(r"\d+", review_text).group()
        except AttributeError:
            db['popcorn'] = "NA"

        db['oscar'] = bool(review.find("div", class_ = "oscar-badge"))
        return db

    def csv(self):
        master = [self.title, self.year, self.imdb_id, self.imdb_rating, self.runtime, self.imdb_cast, self.imdb_votes, self.oscar_winner]

        # not all movies have reviews from Gregg and Tim
        try:
            master += [self.reviews['Gregg']['popcorn'], self.reviews['Gregg']['oscar']]
        except KeyError:
            master += ["NA", "NA"]

        try:
            master += [self.reviews['Tim']['popcorn'], self.reviews['Tim']['oscar']]
        except KeyError:
            master += ["NA", "NA"]

        return master

if __name__ == "__main__":
    with open("data.csv", "w") as f:
        master_csv = "season,episode,airdate,hosts,youtube_id, view_count,like_count,dislike_count,title,year,imdb_id,imdb_rating,runtime,imdb_cast,imdb_votes,oscar_winner,gregg_popcorn,gregg_oscar,tim_popcorn,tim_oscar"
        f.write(master_csv + '\n')

    for season in range(1, 12):
        for episode_index in range(1, 11):
            print(f"{season}-{episode_index}")
            episode = Episode(f"https://oncinematimeline.com/season-{season}/episode-{episode_index}")
            episode.get_youtube()
            episode.write_csv("data.csv")



