# Python 3.3.x
# Requires Praw:
# Requires httplib2: http://code.google.com/p/httplib2/

import time
import praw
import httplib2
import logging
import json
from collections import OrderedDict

# Custom exception
class MyException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

# Reply to comment
def replyToComment(comment, reply):
    comment.reply(reply)
    
    # Add the comment to the already_done list and file
    already_done.append(comment.id)
    f = open('already_done.txt', 'a')
    f.write(comment.id + '\n')
    f.close()
    print(comment.id)


# Riot API Keys
api_key2 = 'e46627f1-4a8c-4392-b28b-bac44de91be9'
api_key = '246bd96f-c140-460c-816c-b0016cc32bf3'

# Riot API
api_url = 'http://prod.api.pvp.net/api/'
availableRegions = ['euw', 'eune', 'na']

# Logging config
logging.basicConfig(filename='log.txt')

# PRAW Reddit config
r = praw.Reddit('ScryingBot by /u/yummypraw v0.1')
r.login(username='yummypraw', password='shoesandsocks')

prawWords = ['!info']

f = open('already_done.txt', 'r')
already_done = f.read().splitlines()
f.close()

# Setup http
h = httplib2.Http('.cache')


# summoner = 'sonumber9'
# region = 'na'
# champion = 'ahri'



print('Running bot')
iterations = 0
while True:
    try:
        subreddit = r.get_subreddit('sandbox')
        subreddit_comments = subreddit.get_comments()
        for comment in subreddit_comments:
            text = comment.body.lower()
            # Check the comment for prawWords
            has_praw = any(string in text for string in prawWords)

            # Check if the comment is in the already_done list
            if has_praw and comment.id not in already_done:
                # Split up the comment to find parameters
                c = comment.body.splitlines()[0][6:]
                parameters = c.split(',')
                summoner = parameters[0]
                region = ''
                champion = ''
                if len(parameters) > 1:
                    # Check if region is supported
                    if parameters[1].lstrip().lower() in availableRegions:
                        region = parameters[1].lstrip().lower()
                    else:
                        reply = 'That region is not supported.'
                        replyToComment(comment,reply)
                        raise MyException('Region not supported')

                if len(region) < 2:
                    region = 'na'
                if len(parameters) > 2:
                    champion = parameters[2].lstrip()

                print('"'+summoner+'"')
                print(region)
                # Use Riot API 

                # Get Summoner ID
                response, content = h.request(api_url + 'lol/' + region + '/v1.1/' + 'summoner/by-name/' + summoner + '?api_key=' + api_key)
                # Check if summoner exists, if not raise exception
                if response.status == 404:
                    reply = 'That summoner does not exist.'
                    replyToComment(comment, reply)
                    raise MyException('Summoner not found')

                content = json.loads(content.decode('utf-8'))
                sid = str(content['id'])
                summoner = content['name']


                # Get SoloQueue Wins/Losses
                response, content = h.request(api_url + 'lol/' + region + '/v1.1/' + 'stats/by-summoner/' + sid + '/summary?api_key=' + api_key)
                content = json.loads(content.decode('utf-8'))

                # This is in case RankedSolo5x5 is not always [3]
                rWins = [summary["wins"] for summary
                          in content["playerStatSummaries"]
                          if summary["playerStatSummaryType"] == "RankedSolo5x5"][0]
                rLosses = [summary["losses"] for summary
                          in content["playerStatSummaries"]
                          if summary["playerStatSummaryType"] == "RankedSolo5x5"][0]

                # rankedStats = content['playerStatSummaries'][3]
                # rWins = rankedStats['wins']
                # rLosses = rankedStats['losses']
                print(rWins)
                print(rLosses)

                # Get Tier, Division and LP
                response, content = h.request(api_url + region + '/v2.1/' + 'league/by-summoner/' + sid + '?api_key=' + api_key)
                content = json.loads(content.decode('utf-8'))
                for entry in content[sid]['entries']:
                    if entry['playerOrTeamId'] == sid:
                        tier = entry['tier']
                        rank = entry['rank']
                        lp = entry['leaguePoints']
                        break
                print(tier)
                print(rank)
                print(lp)

                # Get Top Played Champs
                response, content = h.request(api_url + 'lol/' + region + '/v1.1/' + 'stats/by-summoner/' + sid + '/ranked?api_key=' + api_key)
                content = json.loads(content.decode('utf-8'))
                champs = {}
                for champ in content['champions']:
                    if champ['id'] != 0:
                        for item in champ['stats']:
                            if item['name'] == 'TOTAL_SESSIONS_PLAYED':
                                sessions = item['value']
                                break
                        champs[sessions] = champ['name']
                topPlayedChamps = OrderedDict(sorted(champs.items(), reverse=True)[:3])
                print(list(topPlayedChamps.items())[0][1])
                print(list(topPlayedChamps.items())[0][0])

                # Reply here
                reply = 'Summoner:\n\n    ' + summoner + '\n\n'
                reply += 'Region:\n\n    ' + region.upper() + '\n\n'
                reply += 'Stats:\n\n    ' + tier + ' ' + rank + ' ' + str(lp) + 'LP (' + str(rWins) + ':' + str(rLosses) + ')\n\n'
                reply += 'Most Played Champions:\n\n'
                reply += '    ' + list(topPlayedChamps.items())[0][1] + '(' + str(list(topPlayedChamps.items())[0][0]) + ')\n\n'
                reply += '    ' + list(topPlayedChamps.items())[1][1] + '(' + str(list(topPlayedChamps.items())[1][0]) + ')\n\n'
                reply += '    ' + list(topPlayedChamps.items())[2][1] + '(' + str(list(topPlayedChamps.items())[2][0]) + ')\n\n'


                if len(champion) > 0:
                    reply += 'Champion: ' + champion + '\n\n'

                print(reply)
                replyToComment(comment, reply)
    except MyException as e:
        print(e.value)

    except Exception as e:
        print('Unexpected error occured')
        logging.exception(e)
        with open('log.txt', 'a') as f:
            f.write('\n\n\n')
    iterations += 1
    print('Iterations done: ' + str(iterations))
    time.sleep(300)

