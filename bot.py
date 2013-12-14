# Scrying Bot
# By Ted Chen (sonumber9)
# A Reddit bot which uses the Riot API to automatically
# reply to comments asking for League of Legends summoner
# information and statistics.

# Python 3.3.x
# Requires PRAW: https://praw.readthedocs.org/
# Requires httplib2: http://code.google.com/p/httplib2/

import time
import praw
import httplib2
import logging
import json
from collections import OrderedDict
import datetime

# Reply to comment
def replyToComment(comment, reply):
    # reply += "\n\n---\n\nHi! I'm ScryingBot, I reply with League of Legends summoner stats. To summon me, start a comment with one of the following commands:\n\n    !info summonername, region\n\n    !info summonername, region, championname\n\nI currently only support NA, EUW, and EUNE.\n\nI'm still in development, so send me a PM if you spot any errors or would like to give me some feedback.\n\n*Please be patient with me, I may not be able to respond to every query at this time because of Riot API call limits.*\n\n"
    
    reply += "\n\n---\n\n"
    reply += "- Hi! I'm ScryingBot, I reply with League of Legends summoner stats.\n\n"
    reply += "- [How to summon me](http://www.reddit.com/r/ScryingBot/comments/1sqtbc/scryingbot_command_list/) (Only NA, EUW and EUNE supported currently)\n\n"
    reply += "- See any errors? Want to make a suggestion? [PM me!](http://www.reddit.com/message/compose/?to=ScryingBot)\n\n"
    reply += "- *Test me without spamming /r/leagueoflegends [here.](http://www.reddit.com/r/ScryingBot/comments/1sqwdt/test_scryingbot_here/)*"

    print(reply)
    comment.reply(reply)  
    # Add the comment to the already_done list and file
    already_done.append(comment.permalink)
    f = open('already_done.txt', 'a')
    f.write(comment.permalink + '\n')
    f.close()
    print(comment.permalink)

# Custom exception
class MyException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def parseComments(subreddit):
    try:
        subreddit = r.get_subreddit(subreddit)
        subreddit_comments = subreddit.get_comments()
        for comment in subreddit_comments:
            text = comment.body.lower()
            # Check the comment for prawWords
            has_praw = any(string in text.splitlines()[0] for string in prawWords)

            # Check if the comment is in the already_done list
            if has_praw and comment.permalink not in already_done:
                # Split up the comment to find parameters
                c = comment.body.splitlines()[0][6:]
                parameters = c.split(',')
                summoner = parameters[0].replace(" ", "")

                region = ''
                champion = ''
                if len(parameters) > 1:
                    # Check if it's a region
                    if (len(parameters[1].strip().lower()) > 4) or (parameters[1].strip().lower() == 'vi') or (parameters[1].strip().lower() == 'lux'):
                        # 2nd parameter is a champion
                        champion = parameters[1].strip()
                    else:
                        # Check if region is supported
                        if parameters[1].strip().lower() in availableRegions:
                            region = parameters[1].strip().lower()
                        else:
                            region = parameters[1].strip().lower()
                            reply = 'The region, "' + region + '" is not supported.'
                            replyToComment(comment,reply)
                            raise MyException(reply)

                if len(region) < 2:
                    region = 'na'
                if len(parameters) > 2:
                    champion = parameters[2].strip()

                if len(champion) > 0:
                    # Rename the champion to match Riot's API
                    for champ in championTuple:
                        if champion.lower() == champ[0].lower():
                            champion = champ[1]



                print('"'+summoner+'"')
                print(region)
                print(champion)

                # Use Riot API 

                # Get Summoner ID
                response, content = h.request(api_url + 'lol/' + region + '/v1.1/' + 'summoner/by-name/' + summoner + '?api_key=' + api_key)
                # Check if summoner exists, if not raise exception
                if response.status == 404:
                    reply = 'Summoner "' + summoner + '" was not found in ' + region.upper() + '.'
                    replyToComment(comment, reply)
                    raise MyException(reply)
                elif response.status == 500:
                    reply = 'Summoner "' + summoner + '" was not found. Riot API Internal Server Error.'
                    replyToComment(comment, reply)
                    raise MyException(reply)
                elif response.status == 503:
                    reply = 'Riot API Service for ' + region.uppper() + ' is currently unavailable.'
                    replyToComment(comment, reply)
                    raise MyException(reply)
                elif response.status == 429:
                    reply = "I'm currently overloaded. Please try again in a few minutes."
                    replyToComment(comment, reply)
                    raise MyException(reply)

                content = json.loads(content.decode('utf-8'))
                sid = str(content['id'])
                summoner = content['name']
                
                print(sid)
                # Get SoloQueue Wins/Losses
                try:
                    response, content = h.request(api_url + 'lol/' + region + '/v1.1/' + 'stats/by-summoner/' + sid + '/summary?api_key=' + api_key)
                    if response.status == 429:
                        reply = "I'm currently overloaded. Please try again in a few minutes."
                        replyToComment(comment, reply)
                        raise MyException(reply)
                    content = json.loads(content.decode('utf-8'))

                    rWins = [summary["wins"] for summary
                              in content["playerStatSummaries"]
                              if summary["playerStatSummaryType"] == "RankedSolo5x5"][0]
                    rLosses = [summary["losses"] for summary
                              in content["playerStatSummaries"]
                              if summary["playerStatSummaryType"] == "RankedSolo5x5"][0]
                    print(rWins)
                    print(rLosses)
                except IndexError as e:
                    print('No ranked 5v5')
                    try:
                        # No Ranked 5v5 Games
                        nWins = [summary["wins"] for summary
                                  in content["playerStatSummaries"]
                                  if summary["playerStatSummaryType"] == "Unranked"][0]
                        nLosses = [summary["losses"] for summary
                                  in content["playerStatSummaries"]
                                  if summary["playerStatSummaryType"] == "Unranked"][0]
                        unranked = True
                        print(nWins)
                        print(nLosses)
                    except IndexError as e:
                        # No Unranked 5v5 Games
                        unranked = False

                    response, content = h.request(api_url + 'lol/' + region + '/v1.1/' + 'summoner/' + sid + '?api_key=' + api_key)
                    if response.status == 429:
                        reply = "I'm currently overloaded. Please try again in a few minutes."
                        replyToComment(comment, reply)
                        raise MyException(reply)
                    content = json.loads(content.decode('utf-8'))
                    level = content['summonerLevel']

                    reply = '**Summoner:** ' + summoner + '\n\n'
                    reply += '**Region:** ' + region.upper() + '\n\n'
                    reply += '**Unranked Stats:** ' + 'Level ' + str(level) + ', '
                    
                    if unranked:
                        # reply += str(nWins) + 'W:' + str(nLosses) + 'L\n\n'
                        reply += str(nWins) + 'W\n\n'
                    else:
                        reply += 'No Unranked 5v5 Games Played\n\n'
                    reply += 'No Ranked Solo 5v5 Games Played\n\n'
                    
                    print(reply)
                    replyToComment(comment, reply)
                    raise MyException('No Ranked Solo 5v5 Games Played')

                # Get Tier, Division and LP
                response, content = h.request(api_url + region + '/v2.1/' + 'league/by-summoner/' + sid + '?api_key=' + api_key)
                leaguesError = ''
                if response.status == 503:
                    # Riot Service Unavailable
                    leaguesError =  'Riot Leagues API Currently Unavailable.\n\n'
                elif response.status == 500:
                    leaguesError = 'Riot API Internal Server Error.\n\n'
                elif len(content) < 5:
                    leaguesError = 'Currently Seeding.\n\n'
                elif response.status == 429:
                    reply = "I'm currently overloaded. Please try again in a few minutes."
                    replyToComment(comment, reply)
                    raise MyException(reply)
                else:
                    content = json.loads(content.decode('utf-8'))
                    for entry in content[sid]['entries']:
                        if entry['playerOrTeamId'] == sid:
                            tier = entry['tier']
                            rank = entry['rank']
                            lp = entry['leaguePoints']
                            break
                # print(tier)
                # print(rank)
                # print(lp)

                # Get Top Played Champs
                response, content = h.request(api_url + 'lol/' + region + '/v1.1/' + 'stats/by-summoner/' + sid + '/ranked?api_key=' + api_key)
                if response.status == 429:
                    reply = "I'm currently overloaded. Please try again in a few minutes."
                    replyToComment(comment, reply)
                    raise MyException(reply)
                content = json.loads(content.decode('utf-8'))
                champs = {}
                for champ in content['champions']:
                    if champ['id'] != 0:
                        for item in champ['stats']:
                            if item['name'] == 'TOTAL_SESSIONS_PLAYED':
                                sessions = item['value']
                                break
                        if champ['id'] == 72:
                            champs[sessions] = 'Skarner'
                        else:
                            champs[sessions] = champ['name']
                topPlayedChamps = list(OrderedDict(sorted(champs.items(), reverse=True)[:3]).items())
                # print(topPlayedChamps[0][1])

                if len(champion) > 0:
                    print(champion)
                    
                    champFound = False
                    for champ in content['champions']:
                        if champ['id'] != 0:
                            if champ['name'].lower() == champion.lower():
                                for stat in champ['stats']:
                                    if stat['name'] == 'TOTAL_SESSIONS_WON':
                                        cWins = stat['value']
                                    elif stat['name'] == 'TOTAL_SESSIONS_LOST':
                                        cLosses = stat['value']
                                    elif stat['name'] == 'TOTAL_CHAMPION_KILLS':
                                        cK = stat['value']
                                    elif stat['name'] == 'TOTAL_DEATHS_PER_SESSION':
                                        cD = stat['value']
                                    elif stat['name'] == 'TOTAL_ASSISTS':
                                        cA = stat['value']
                                    elif stat['name'] == 'TOTAL_SESSIONS_PLAYED':
                                        cP = stat['value']
                                aK = cK/cP
                                aD = cD/cP
                                aA = cA/cP
                                winRatio = cWins/cP*100

                                champion = champ['name']

                                # print(format(aK, '.1f'))
                                # print(format(aD, '.1f'))
                                # print(format(aA, '.1f'))
                                # print(format(winRatio, '.1f'))
                                champFound = True
                                break

                # Reply here
                reply = '**Summoner:** ' + summoner + '\n\n'
                reply += '**Region:** ' + region.upper() + '\n\n'
                if len(leaguesError) > 0:
                    reply += '**Ranked Stats:** ' + leaguesError
                else:
                    reply += '**Ranked Stats:** ' + tier + ' ' + rank + ' ' + str(lp) + 'LP (' + str(rWins) + 'W:' + str(rLosses) + 'L)\n\n'
                reply += '**Most Played Champions:** '
                try:
                    reply += topPlayedChamps[0][1] + ' (' + str(topPlayedChamps[0][0]) + ')'
                except IndexError as e:
                    reply += 'No champions played\n\n'
                try:
                    reply += ', ' + topPlayedChamps[1][1] + ' (' + str(topPlayedChamps[1][0]) + ')'
                    reply += ', ' + topPlayedChamps[2][1] + ' (' + str(topPlayedChamps[2][0]) + ')\n\n'
                except IndexError as e:
                    pass


                # reply += '    ' + '[](/' + topPlayedChamps [0][1] + ')' + topPlayedChamps[0][1] + '(' + str(topPlayedChamps[0][0]) + ')\n\n'
                # reply += '    ' + '[](/' + topPlayedChamps [1][1] + ')' + topPlayedChamps[1][1] + '(' + str(topPlayedChamps[1][0]) + ')\n\n'
                # reply += '    ' + '[](/' + topPlayedChamps [2][1] + ')' + topPlayedChamps[2][1] + '(' + str(topPlayedChamps[2][0]) + ')\n\n'



                if len(champion) > 0:
                    # Rename the champion to match normal usage
                    for champ in championTuple:
                        if champion.lower() == champ[1].lower():
                            print(champion)
                            champion = champ[0]
                            print(champion)
                    # Add champion stats to reply
                    if champFound:
                        reply += '**Champion:** '
                        reply += champion + ' (' + str(cP) + '), '
                        reply += str(cWins) + 'W:' + str(cLosses) + 'L (' + format(winRatio, '.1f') + '%), '
                        reply += format(aK, '.1f') + '/' + format(aD, '.1f') + '/' + format(aA, '.1f') + ' (Average K/D/A)\n\n'
                    else:
                        reply += 'Either the champion, ' + champion + ', does not exist or the summoner, ' + summoner + ', has not played ' + champion + ' in ranked.\n\n'

                print('REPLY:')
                print(reply)
                replyToComment(comment, reply)
    except MyException as e:
        print(e.value)
        # Logs exceptions
        with open('log.txt', 'a') as f:
            f.write(str(datetime.datetime.now()) + '\n')
            f.write(e.value + '\n\n\n')
    # except KeyError as e:
    #     print(response)
    #     reply = "I'm currently overloaded. Please try again in a few minutes."
    #     replyToComment(comment, reply)
    #     raise MyException(reply)
    except Exception as e:

        # Logs exceptions
        print('Unexpected error occured')
        try:
            with open('log.txt', 'a') as f:
                f.write(str(datetime.datetime.now()) + '\n')
                f.write(summoner + '/' + region + '/' + champion + '\n')
                f.write(sid + '\n')
                f.write(comment.permalink + '\n')
        except Exception as e:
            pass
        logging.exception(e)
        with open('log.txt', 'a') as f:
            f.write('\n\n\n')
        # Add comment to backlog

testMode = False

# Riot API Keys
api_key = 'e46627f1-4a8c-4392-b28b-bac44de91be9'
api_key2 = '246bd96f-c140-460c-816c-b0016cc32bf3'

# Riot API
api_url = 'http://prod.api.pvp.net/api/'
availableRegions = ['euw', 'eune', 'na']
championTuple = [("Cho'Gath",'Chogath'), ('Dr. Mundo','DrMundo'),('Dr.Mundo','DrMundo'), ('Jarvan IV','JarvanIV'),('Jarvan','JarvanIV'), ("Kha'Zix",'Khazix'), ("Kog'Maw","KogMaw"), ('Lee Sin', 'LeeSin'), ('Master Yi', 'MasterYi'), ('Miss Fortune', 'MissFortune'), ('Twisted Fate','TwistedFate'), ('Wukong','MonkeyKing')]

# Logging config
logging.basicConfig(filename='log.txt')

# PRAW Reddit config
r = praw.Reddit('ScryingBot by /u/ScryingBot v0.8')

if testMode:
    r.login(username='yummypraw', password='abcd1234')
    subreddit = 'sandbox'
else:
    r.login(username = 'ScryingBot')
    subreddit = 'leagueoflegends+scryingbot'

prawWords = ['!info']

f = open('already_done.txt', 'r')
already_done = f.read().splitlines()
f.close()

# Setup http
h = httplib2.Http('.cache')


# Run the bot
print('Running bot')
iterations = 0
while True:
    parseComments(subreddit)
    iterations += 1
    print('Iterations done: ' + str(iterations))
    time.sleep(40)

