# Created: November 18, 2022
# Author: Brendan Keane (GitHub @brendanwilliam)
# Purpose: Crawl NBA.com pages to pull shotchart data and save as JSON

# Imports
from bs4 import BeautifulSoup
import os
import requests
import json
import time
import random

#==================== Global constants ====================#

# URL beginning and end to access pages with shot charts
URL_START = "https://www.nba.com/game/00"
URL_END = "/game-charts"

# Base number for game URLs (2022-2023 season) and total games for the season
# Note: Each game URL increments by 1 from `22200001` to `22201230`
GAME_NUM_BASE = 22200001
TOTAL_GAMES = 1230

# All game URLs for 2022-2023 season
URL_LIST = []
for game in range(TOTAL_GAMES):
  req_url = URL_START + str(GAME_NUM_BASE + game) + URL_END
  URL_LIST.append(req_url)

# Request headers
HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

# Export directory path
EXPORT_PATH = "../src/data/raw/"


#==================== Functions ====================#

# Returns Soup version for a given URL
def get_soup(url):
  try:
    req = requests.get(url, HEADERS)
    return BeautifulSoup(req.text, "lxml")
  except:
    print("Unable to retrieve information from given URL:\n\t" + url)

# Returns content with id='__NEXT_DATA__' which contains playByPlay JSON
def get_script(soup):
  try:
    return soup.find(id='__NEXT_DATA__')
  except:
    print("Unable to retrieve script with id=\'__NEXT_DATA__\'")
    print("Given function data:\n\t" + soup)

# Returns play-by-play JSON from page script
def get_playbyplay(elem):
  try:
    temp_json = json.loads(elem.text)
    return temp_json['props']['pageProps']['playByPlay']['actions']
  except:
    print("Unable to retrieve play-by-play data")
    print("Given function data:\n\t" + elem)

# Saves play-by-play as a JSON in ./src/data/playbyplay directory
def save_playbyplay(obj, game_num):
  try:
    if (len(obj) > 0):
      # Export path formated as "S[start YY + end YY]-G[4-digit game number]"
      print("Exporting GAME " + "{0:0=4d}".format(game_num))
      export_path = EXPORT_PATH + "S2223-G" + "{0:0=4d}".format(game_num) + ".json"
      export_obj = json.dumps(obj, indent=4)
      with open(export_path, "w") as outfile:
        outfile.write(export_obj)
  except:
    print("Data not available for game " + str(game_num))

# Exports a single game page. "game_num" ranges from 1 to 1230, returning the
# "n"th game of the season.
def export_game(game_num):
  try:
    # Gets Soup for the given page
    random_sleep(1, 3)
    soup = get_soup(URL_LIST[game_num - 1])

    # Pulls page script within id='__NEXT_DATA__' tag
    random_sleep(1, 3)
    script = get_script(soup)

    # Pulls play-by-play JSON from script
    random_sleep(1, 3)
    playbyplay = get_playbyplay(script)

    # Saves play-by-play JSON in ./src/data/playbyplay directory
    save_playbyplay(playbyplay, game_num)

  except:
    print("Unable to get data from game: " + str(game_num))

# Makes program sleep for a random amount of seconds between `min` and `max`
def random_sleep(min, max):
  time.sleep(random.randint(min*1000, max*1000) / 1000)

# Exports all available games for the 2022-2023 season
def export_all_games(start = 0, end = TOTAL_GAMES):
  num_fails = 0 # Number of failed attempts
  if (start == 0):  # If no parameters, sets beginning to first unexported game
    start = len(os.listdir(EXPORT_PATH))
  try:
    # Iterates through games
    for game in range(start, end):

      # Checks number of games before and after export
      cur_games = len(os.listdir(EXPORT_PATH))
      export_game(game + 1)
      new_games = len(os.listdir(EXPORT_PATH))

      # If no new games were exported, increments number of failed attempts
      if (cur_games == new_games):
        num_fails += 1
        print("Export for game " + "{0:0=4d}".format(game + 1) + " was unsuccessful")
        print("Unsuccessful attempt: " + str(num_fails) + " of 3\n")
        print("Trying again...\n")
        game -= 1

      # If 3 failed attempts, breaks loop
      if (num_fails == 3):
        print("================================")
        print("Exited program on game " + "{0:0=4d}".format(game + 1))
        print("================================")
        break
  except:
    print("Unable to retrieve game data within the following range:\n\tStart: "
    + str(start) + "\tEnd: " + str(end))


#==================== Main ====================#
if __name__ == "__main__":
  export_all_games()