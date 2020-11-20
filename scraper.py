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
        # try:
        self.next_episode = self.soup.find("a", class_="next-ep").get("href")
        # except Exception:
        #     self.next_episode = None
    def get_movies(self):
        movies = self.soup.find("div", "episode-movies").find_all("div", recursive = False)
        movies = [Movie(soup) for soup in movies]
            

    

class Movie:
    def __init__(self, soup):
        self.soup = soup
        self.title = self.soup.find("p", class_ = "movie-title").text
        self.year = re.match(r"\d+", self.soup.find(text="Year: ").next).group()
        print(year)

class MovieReview:
    def __init__(self, soup):
        self.soup = soup
        # self.author = self.find("div", class_ = "review-info").p
        self.author = self.find("p", class="title").text
        self.popcorn = self.find("p", class="rating-summary").text
        

start = Episode("https://oncinematimeline.com/season-1/episode-1")
print(start.airdate)
print(start.hosts)
print(start.next_episode)
print(start.season)
print(start.episode)
start.get_movies()

