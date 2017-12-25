import _pickle
import re
import glob
import numpy as np

from util import printt

contestant_stats_headers = ["j_score", "dj_score", "fj_score", "coryat_score", "R", "W", "Rebs", "DDs", "DD_gainloss", "fj", "fj_gainloss", "ba", "tba"] 
headers = ["contestant", "cont_raw", "occupation", "location", "game_raw", "game", "airdate"] + contestant_stats_headers

chars = {
    '\xc2\x82' : ',',        # High code comma
    '\xc2\x84' : ',,',       # High code double comma
    '\xc2\x85' : '...',      # Tripple dot
    '\xc2\x88' : '^',        # High carat
    '\xc2\x91' : '\x27',     # Forward single quote
    '\xc2\x92' : '\x27',     # Reverse single quote
    '\xc2\x93' : '\x22',     # Forward double quote
    '\xc2\x94' : '\x22',     # Reverse double quote
    '\xc2\x95' : ' ',
    '\xc2\x96' : '-',        # High hyphen
    '\xc2\x97' : '--',       # Double hyphen
    '\xc2\x99' : ' ',
    '\xc2\xa0' : ' ',
    '\xc2\xa6' : '|',        # Split vertical bar
    '\xc2\xab' : '<<',       # Double less than
    '\xc2\xbb' : '>>',       # Double greater than
    '\xc2\xbc' : '1/4',      # one quarter
    '\xc2\xbd' : '1/2',      # one half
    '\xc2\xbe' : '3/4',      # three quarters
    '\xca\xbf' : '\x27',     # c-single quote
    '\xcc\xa8' : '',         # modifier - under curve
    '\xcc\xb1' : '',         # modifier - under line
    u'\xa0'    : ' ',
    u'\u2018'  : "'",
    u'\u2019'  : "'",
    u'\u2013'  : "-",
}
def replace_chars(match):
    char = match.group(0)
    return chars[char]
subst_str = "(" + "|".join(chars.keys()) + ")"



def read_cont_season():
    fils = glob.glob("./Season_*_contestants.cpkl")
    # determine number of games total:
    n_games = 0
    for fil in fils:
        conts = _pickle.load(open(fil, 'rb'))
        for name in conts.keys():
            n_games += len(conts[name]["games"])
    cont_games = np.empty([n_games, len(headers)], dtype="U150")
    i = 0 
    for fil in fils:
        printt("Processing {}".format(fil))
        conts = _pickle.load(open(fil, 'rb'))
        for name in conts.keys():
            cont = conts[name]
            desc = cont["desc"]
            try:
                occup, loc = desc.split(" from ")
            except:
                occup = loc = ""
            for game in cont["games"]:
                try:
                    game_num, airdate = game[0].split(", aired\xa0")
                except:
                    game_num = airdate = ""
                new_row =  [name, occup, loc, desc, game[0], game_num, airdate] + game[1:]
                new_row = [re.sub(subst_str, replace_chars, elem).replace(",","") for elem in new_row]
                cont_games[i,:] = new_row
                i += 1
    return cont_games


def main():
    cont_games = read_cont_season()
    np.savetxt("contestant_games.csv", cont_games, fmt="%s", delimiter=",", header=",".join(headers))

    import pdb; pdb.set_trace()


if __name__ == "__main__":
    main()
