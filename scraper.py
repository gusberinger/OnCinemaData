import requests
from bs4 import BeautifulSoup
import re
import csv
from imdb import IMDb


ia = IMDb()
# fill in data from oncinematimeline that does not match imdb
imdb_na = {"Escape from Planet Earth": "0765446",
           "Scary Movie 5": "0795461",
           "Sin City: A Dame to Kill For": "0458481",
           "No Escape (aka The Coup)": "1781922",
           "The Moon and the Sun": "2328678",
           "Star Trek Beyond": "2660888",
           "Fast & Furious 8": "4630562",
           "Acrimony": "6063050"}

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
        self.airdate = self.soup.find("h5", text = "Original Air Date").parent.p.text
        hosts = self.soup.find("h5", text="Hosts / Guests").parent.find_all("div")
        self.hosts = [item.text for item in hosts]
        movies = self.soup.find("div", "episode-movies").find_all("div", recursive = False)
        self.movies = [Movie(soup) for soup in movies]


    def write_csv(self, file_name):
        with open(file_name, "a", newline="") as f:
            writer = csv.writer(f)
            for movie in self.movies:
                row = [self.season, self.episode, self.airdate] + movie.csv()
                writer.writerow(row)

class Movie:
    def __init__(self, soup):
        self.soup = soup
        self.title = self.soup.find("p", class_ = "movie-title").text
        self.year = re.match(r"\d+", self.soup.find(text="Year: ").next).group()
        self.reviews = {}
        self.reviews['Gregg'] = {}
        self.reviews['Tim'] = {}
        reviews_soup = soup.find("div", class_= "row reviews").find_all("div", class_ = "review-info")
        # go up two levels to see oscar information
        reviews_soup = [x.parent.parent for x in reviews_soup]
        for review in reviews_soup:
            author = review.find("p", class_ = "title").text
            author = re.match(r"(\w+)'s Review", author).group(1)
            self.reviews[author] = self.build_review_db(review)


        # not all data on website matches imdb
        if self.title in imdb_na.keys():
            self.imdb_id = imdb_na[self.title]
            imdb_movie = ia.get_movie(self.imdb_id)
        else:
            imdb_movie = ia.search_movie(f"{self.title} ({self.year})")[0]

        ia.update(imdb_movie, 'main')
        self.imdb_rating = imdb_movie['rating']
        self.imdb_id = imdb_movie.getID()


        try:
            self.runtime = imdb_movie['runtime'][0]
        except Exception:
            self.runtime = "NA"
        try:
            self.imdb_votes = imdb_movie['votes']
        except Exception:
            self.imdb_votes = "NA"



        self.oscar_winner = self.imdb_id in winners

    def build_review_db(self, review):
        """Build a database of information for each review"""
        db = {}
        try:
            review_text = review.find("p", class_ = "rating-summary").text
            db['popcorn'] = re.match(r"\d+", review_text).group()
        except AttributeError:
            db['popcorn'] = "NA"

        if review.find("div", class_ = "oscar-badge"):
            db['oscar'] = "True"
        else:
            db['oscar'] = "False"

        return db

    def csv(self):
        master = [self.title, self.year, self.imdb_id, self.imdb_rating, self.runtime, self.imdb_votes, self.oscar_winner]
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
        master_csv = "season,episode,airdate,title,year,imdb_id,imdb_rating,runtime,imdb_votes,oscar_winner,gregg_popcorn,gregg_oscar,tim_popcorn,tim_oscar"
        f.write(master_csv + '\n')

    for season in range(1, 12):
        for episode_index in range(1, 11):
            print(f"{season}-{episode_index}")
            episode = Episode(f"https://oncinematimeline.com/season-{season}/episode-{episode_index}")
            episode.write_csv("data.csv")



