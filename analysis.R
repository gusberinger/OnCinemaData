library(car)
library(tidyverse)

data <- read.csv("data.csv")
data <- data %>% mutate(gregg_oscar = as.logical(gregg_oscar),
                tim_oscar = as.logical(tim_oscar))

cor(data$gregg_popcorn, data$tim_popcorn, use = "pairwise.complete.obs")
summary(lm(gregg_popcorn~tim_popcorn, data = data))


data %>% ggplot(aes(x = airdate)) +
  geom_point(aes(y = gregg_popcorn), color = "blue") +
  geom_point(aes(y = tim_popcorn), color = "red")
  
model <- lm(gregg_popcorn~gregg_oscar, data = data)
summary(model)
cor(data$gregg_oscar, data$tim_oscar)
