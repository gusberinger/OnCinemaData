import pandas as pd

data = pd.read_csv("data.csv")

reddawn = data[data["title"] == "Red Dawn"]

assert list(reddawn.gregg_popcorn)[0] == 4
assert list(reddawn.tim_popcorn)[0] == 5
assert list(reddawn.oscar_winner)[0] == False
assert list(reddawn.hosts)[0] == "Gregg Turkington,Tim Heidecker"

anna = data[data["title"] == "Anna Karenina"]

assert list(anna.runtime)[0] == 129
assert list(anna.gregg_oscar)[0] == True
assert list(anna.oscar_winner)[0] == True
assert list(anna.imdb_id)[0] == 1781769

