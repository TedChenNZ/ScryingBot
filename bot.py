# Python 3.3.x
# Requires Praw:
# Requires httplib2: http://code.google.com/p/httplib2/

import time
import praw
import httplib2
import logging

api_key = 'e46627f1-4a8c-4392-b28b-bac44de91be9'
api_key2 = '246bd96f-c140-460c-816c-b0016cc32bf3'

logging.basicConfig(filename='log.txt')


r = praw.Reddit('ScryingBot by /u/yummypraw v0.1')
r.login(username='yummypraw', password='shoesandsocks')

prawWords = ['!lolinfo', '!info']

f = open('already_done.txt', 'r')
already_done = f.read().splitlines()
f.close()

h = httplib2.Http('.cache')


print('Running bot')
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
                champion = ''
                if len(parameters) > 1:
                    champion = parameters[1]

                # Riot API
                response, content = h.request('http://prod.api.pvp.net/api/lol/na/v1.1/summoner/by-name/SoNumber9?api_key=' + api_key)
                print(content)

                # Reply here
                reply = 'Summoner: ' + summoner + '\n\n'
                if len(champion) > 0:
                    reply += 'Champion: ' + champion + '\n\n'


                comment.reply(reply)
                
                # Add the comment to the already_done list and file
                already_done.append(comment.id)
                f = open('already_done.txt', 'a')
                f.write(comment.id + '\n')
                f.close()
                print(comment.id)
    except Exception as err:
        logging.exception(err)
        with open('log.txt', 'a') as f:
            f.write('\n\n\n')

    time.sleep(300)





# import praw

# user_agent = ("Karma breakdown 1.0 by /u/_Daimon_ "
#               "github.com/Damgaard/Reddit-Bots/")
# r = praw.Reddit(user_agent=user_agent)
# thing_limit = 10
# user_name = "_Daimon_"
# user = r.get_redditor(user_name)
# gen = user.get_submitted(limit=thing_limit)
# karma_by_subreddit = {}
# for thing in gen:
#     subreddit = thing.subreddit.display_name
#     karma_by_subreddit[subreddit] = (karma_by_subreddit.get(subreddit, 0)
#                                      + thing.score)
#     print(subreddit)
#     print(karma_by_subreddit[subreddit])