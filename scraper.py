import requests
from bs4 import BeautifulSoup
import re

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


    def episode_csv(self):
            return f"{self.airdate},{self.season},{self.episode}"

            
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
        
        # simplify author
        for review in reviews_soup:
            author = review.find("p", class_ = "title").text
            if author == "Gregg's Review":
                author = "Gregg"
            elif author == "Tim's Review":
                author = "Tim"
                
            self.reviews[author] = self.build_review_db(review)


    def build_review_db(self, review):
        """Build a database of information for each review"""
        db = {}
        review_text = review.find("p", class_ = "rating-summary").text
        db['popcorn'] = re.match(r"\d+", review_text).group()
        if review.find("div", class_ = "oscar-badge"):
            db['oscar'] = True
        else:
            db['oscar'] = False

        return db

    def movie_csv(self):
        return f"{self.title}"

start = Episode("https://oncinematimeline.com/season-1/episode-1")
print(start.movies[0].reviews)
print(start.movies[1].reviews)

