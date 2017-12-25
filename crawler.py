from os.path import join
import datetime
import requests as rq
from bs4 import BeautifulSoup as soup, element


base_url = "http://www.j-archive.com"
all_seasons_php = "listseasons.php"

## Utility Functions ##
def printt(msg):
   time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   print("{}| {}".format(time_str, msg))


## Data we will be collecting ##
contestants = {}


## Crawling ##
def process_contestant(cont):
    link = cont.find("a")
    name = link.text
    if name not in contestants:
        # get player stats page
        desc = ",".join(cont.text.split(",")[1:])
        pid = link.get("href").split("id=")[1]
        url = join(base_url, "showplayerstats.php?player_id={}".format(pid))
        sup = soup(rq.get(url).text, "lxml")
        # get stats from all games
        games = []
        for tab in sup.find_all("table"):
            for row in tab.children:
                if isinstance(row, element.Tag) and row.text[0] == "#":
                    # this is a game summary
                    game = []
                    for dat in row.children:
                        game.append(dat.text)
                    games.append(game)
        contestants[name] = {"id":pid, "desc":desc, "games":games}
     

def process_episode(episode_link):
    print(episode_link.text)
    episode, _, airdate = episode_link.text.split()
    printt("\tProcessing Episode {}".format(episode))
    php = episode_link.get("href")
    sup = soup(rq.get(php).text, "lxml")
    # Get contestants
    conts = sup.find_all(class_="contestants")
    for cont in conts:
        process_contestant(cont)



def process_season(season_link):
    season = season_link.text
    printt("Processing {}".format(season))
    php = season_link.get("href")
    sup = soup(rq.get(join(base_url, php)).text, "lxml")
    # Get all episodes
    episode_links = [a for a in sup.find_all("a") if "game_id" in a.get("href")]
    for episode_link in episode_links:
        process_episode(episode_link)


## format and store data ##


def main():
    text = rq.get(join(base_url, all_seasons_php)).text

    sup = soup(text, "lxml")

    # get all season links:
    season_links = [a for a in sup.find_all('a') if "Season" in a.text]

    for season_link in season_links:
        process_season(season_link)

    import pdb; pdb.set_trace()


if __name__=="__main__":
    main()
