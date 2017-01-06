from time import gmtime, strftime, sleep
from urllib.request import urlopen
from urllib.error import HTTPError
import json

# files
TEAM_FILE_PATH = "team.txt"
API_KEY_PATH = "api_key.secret"
DATA_ROOT = "data/"

# API constants
API_KEY = open(API_KEY_PATH, "r").read()
API_REGION = "OC1" # oceania
API_ROOT = "https://oce.api.pvp.net/api/lol/oce/v1.3/"
API_ENDPOINT_CURRENT_GAME = API_ROOT + "observer-mode/rest/consumer/getSpectatorGameInfo/" + API_REGION + "/{0}?api_key=" + API_KEY
API_THROTTLE_MAX_REQUESTS = 10 # 10 requests every
API_THROTTLE_WINDOW = 10 # 10 seconds
API_BACKOFF = 60 * 60 # wait an hour if told to back off


def save(summoner_id):
    url = API_ENDPOINT_CURRENT_GAME.format(summoner_id)

    try:
        response = urlopen(url)
    except HTTPError as e:
        if e.code == 404: # nothing there
            return False
        elif e.code == 403: # banned
            print("Banned.")
            quit()
        elif e.code == 429: # back off
            print("Backing off for " + str(API_BACKOFF) + " seconds...")
            sleep(API_BACKOFF)
        

    raw_data = response.read()

    json_data = json.loads(raw_data)

    game_id = json_data["gameId"]
    
    current_time = str(gmtime())

    save_location = DATA_ROOT + "{0}/{1}/{2}.json".format(summoner_id, game_id, current_time)

    with open(save_location, "w") as file:
        file.write(raw_data)

    return True


def listen(summoner_ids):
    requests = 0
    
    while 1:
        for summoner_id in summoner_ids:
            if(save(summoner_id)):
                print(str(requests) + " Pulled " + summoner_id + ".")
            else:
                print(str(requests) + " None found for " + summoner_id + ".")
            requests += 1

            # rate-limiting compliance
            if requests == API_THROTTLE_MAX_REQUESTS:
                print("Waiting for " + str(API_THROTTLE_WINDOW) + " seconds...")
                requests = 0 # reset request counter
                sleep(API_THROTTLE_WINDOW) # wait

        print("\n")

team = [line.rstrip('\n') for line in open(TEAM_FILE_PATH)]

# main loop
listen(team)
