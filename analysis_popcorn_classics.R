library(tidyverse)

popcorn <- read.csv("popcorn_classics.csv")
popcorn <- popcorn %>% mutate(airdate = as.Date(airdate,format="%m/%d/%Y"),
                              index = 10 * (season - 1) + episode)
                        

popcorn.tally <- popcorn %>% group_by(season, episode) %>% count %>% mutate(index = 10 * (season - 1) + episode)
popcorn.tally <- merge(data.frame(popcorn.tally), popcorn) 

popcorn.tally <- ggplot(aes(x = index, y = n)) + geom_point()
popcorn %>% ggplot(aes(x = index, y = imdb_rating, color=season)) +
  geom_point()
