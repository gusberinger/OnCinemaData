library(MASS)
library(tidyverse)
library(splitstackshape)
library(car)
library(sandwich)
library(lmtest)
library(stringr)
library(broom)
library(tidyselect)

data <- read.csv("data.csv")
data <- data %>% mutate(airdate = as.Date(airdate,format="%m/%d/%Y"),
                        imdb_rating_scaled = imdb_rating / 2,
                        like_percentage = like_count / (like_count + dislike_count),
                        host_count = str_count(hosts, "\\|") + 1,
                        season = ordered(season),
                        episode = ordered(episode))

data <- cSplit_e(data, "hosts", "|", type = "character", fill = 0, drop = T)


# what are the most common actors in movies reviewed? -----------



cSplit_e(data, "imdb_cast", "|", type = "character", fill = 0, drop = T) %>%
  select(starts_with("imdb_cast")) %>% summarize_all(sum) %>% t %>% View

# get rid of film data
episodes <- data %>% select(-c(title:tim_oscar), -imdb_rating_scaled) %>%
                     distinct()

# get rid of hosts that appeared less than 5 times
chars <- episodes %>% select(starts_with("hosts_")) %>% 
  summarize_all(sum) %>% select_if(function(x) {return(x<6)}) %>% colnames
episodes <- episodes %>% select(-all_of(chars))
data <- data %>% select(-all_of(chars))

data %>% ggplot(aes(x = airdate)) +
  geom_point(aes(y = gregg_popcorn), color = "blue", alpha=.5) +
  geom_point(aes(y = tim_popcorn), color = "red", alpha = .5) +
  ylab("Popcorn") + xlab("Airdate")

episodes %>% ggplot(aes(x = airdate, y = view_count,
                        color = season)) +
  geom_point() +
  ylab("View Count") + xlab("Airdate") + labs(color = "Season")


episodes %>% ggplot(aes(x = airdate, y = like_percentage, 
                        color = season)) +
  geom_point() +
  ylab("Like Percentage") + xlab("Airdate")

episodes %>% ggplot(aes(x = airdate, y = host_count, 
                        color = season)) +
  ylab("Number of Guests/Hosts") + xlab("Airdate") + labs(color = "Season") +
  geom_point() 


episodes %>% ggplot(aes(x = airdate, y = view_count, 
                        color = factor(`hosts_Axiom Serradimigni`))) +
  ylab("Number of Views") + xlab("Airdate") + labs(color = "Dekkar") +
  geom_point() 

episodes %>% ggplot(aes(x = view_count, y = like_percentage,
                        color = season)) +
  ylab("Like Percentage") + xlab("Views") + labs(color = "Season") +
  geom_point()
