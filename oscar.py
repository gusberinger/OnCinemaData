import csv
from imdb import IMDb
from tqdm import tqdm

ia = IMDb()

new_file = []
with open("wikipedia_oscars.csv", "r", encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=",", quotechar='"')
    for row in tqdm(list(reader)):
        title, year, award, nominations = row
        movie = ia.search_movie(f"{title} ({year})")[0]
        imdb_id = movie.getID()
        new_file.append([title, year, imdb_id])

with open("oscars.csv", "w", newline="", encoding='utf-8') as f:
    writer = csv.writer(f)
    for row in new_file:
        writer.writerow(row)
