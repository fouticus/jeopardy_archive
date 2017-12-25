from os.path import join
import datetime
import _pickle
import requests as rq
from bs4 import BeautifulSoup as soup, element


## Utility Functions ##
def printt(msg):
   time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   print("{}| {}".format(time_str, msg))

    
base_url = "http://www.j-archive.com"


## Crawling ##
def process_contestant(cont, contestants):
    link = cont.find("a")
    name = link.text
    printt("\t\tProcessing Contestant: {}".format(name))
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
     

def process_episode(episode_link, contestants):
    episode, _, airdate = episode_link.text.split()
    printt("\tProcessing Episode {}".format(episode))
    php = episode_link.get("href")
    sup = soup(rq.get(php).text, "lxml")
    # Get contestants
    conts = sup.find_all(class_="contestants")
    for cont in conts:
        process_contestant(cont, contestants)



def process_season(season_link):
    contestants = {}
    season = season_link.text
    printt("Processing {}".format(season))
    php = season_link.get("href")
    sup = soup(rq.get(join(base_url, php)).text, "lxml")
    # Get all episodes
    episode_links = [a for a in sup.find_all("a") 
        if "game_id" in a.get("href") and "aired" in a.text]
    for episode_link in episode_links:
        process_episode(episode_link, contestants)
    with open("{}_contestants.cpkl".format(season.replace(" ", "_")), "wb") as f:
        _pickle.dump(contestants, f)
    contestants = {}


## format and store data ##


def main():
    # starting page
    text = rq.get(join(base_url, "listseasons.php")).text
    sup = soup(text, "lxml")

    # get all season links:
    season_links = [a for a in sup.find_all('a') if "Season" in a.text]

    for season_link in season_links:
        process_season(season_link)

    import pdb; pdb.set_trace()


if __name__=="__main__":
    main()
