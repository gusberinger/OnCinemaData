from scraper import Episode, Movie, Review
import csv


def build_locations():
    with open("onlocation.csv", "w") as f:
        f.write(Episode.header + Episode.location_header + '\n')
        writer = csv.writer(f)
        for season in range(1, 12):
            for index in range(1, 11):
                print(f"{season}-{index}")
                episode = Episode(season, index)
                writer.writerow(episode.location_row())
            
def build_movie_reviews():
    with open("movie_reviews.csv", "w") as f:
        f.write(Episode.header + Movie.header + Review.header + '\n')
        writer = csv.writer(f)
        for season in range(11, 12):
            for index in range(1, 11):
                print(f"{season}-{index}")
                episode = Episode(season, index)
                for row in episode.review_rows():
                    writer.writerow(row) 
             
def build_popcorn_classics():
    with open("popcorn_classics.csv", "w") as f:
        f.write(Episode.header + Movie.header + '\n')
        writer = csv.writer(f)
        for season in range(1, 12):
            for index in range(1, 11):
                print(f"{season}-{index}")
                episode = Episode(season, index)
                for row in episode.classics_rows():
                    writer.writerow(row) 
            
if __name__ == "__main__":
    build_movie_reviews()
                
