library(leaflet)
library(glue)

locations <- read.csv("onlocation.csv")
locations <- locations %>% mutate(airdate = as.Date(airdate,format="%m/%d/%Y"),
                                  season = ordered(season))
locations <- locations %>% drop_na()
locations <- locations %>% mutate(marker.description = glue("<b>{movie} ({year})</b><br>Season {season} Episode {episode}<br><i>{quote}</i><br><img width = 120 src={cover_url}>"))
locations %>% leaflet() %>%
  setView(lat = 34.16163, lng = -117.8592, zoom = 9.5) %>%
  addTiles() %>%  # Add default OpenStreetMap map tiles
  addMarkers(~longitude, ~latitude, popup = ~marker.description)

# data
