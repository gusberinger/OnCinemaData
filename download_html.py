import requests

for season in range(1, 12):
    for index in range(1, 11):
            url = f"https://oncinematimeline.com/season-{season}/episode-{index}"
            page = requests.get(url).content
            with open(f"pages/{season}-{index}.html", "wb") as f:
                f.write(page)
                
