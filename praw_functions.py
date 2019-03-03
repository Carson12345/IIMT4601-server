import praw
import json
import sys 
import time 
import io

DEBUG = 0
PRODUCTION = 0
TIMES = 2
SLEEPTIME = 2
NUMTORETRIEVE = 30
SUBREDDITS = "news+worldnews+funny+movies"

""" NOTE: pip install praw """

"""
to implement:
(1) take system arguments as username and password 
-----------------------------------------------------------------------------------------------
submission update logic: filter out duplicate submissions by (created_utc + id)
a. retain the timestamp and userid of the last saved submission 
b. retrieve a fixed amount of submissions 
c. keep only the ones whose created_utc is later than the lastest (created_utc + author)
d. push new submissions to the queue 
** Number of submission per second is around 2
** Query 50 posts per 10 second could be pretty enough

database update logic: update on alert from submission update 
e. update database with data from queue 

submission update and database update should work as different processes 

"""

# Oath2 for Reddit API usage in read-only mode
# This application is registered to Reddit API as a standalone script running on private server 
def login(username='rebpm', password='NORI12onfire'):
	reddit = praw.Reddit(client_id='eG7xz4xynkS8hw',
                     	client_secret='ghMVADsKO9x0NN8szrgiOtWbrQ4',
                     	password=password,
                     	user_agent='testscript by /u/rebpm',
                     	username=username)
	
	# to verify the current authentication info
	if DEBUG == 1:
		print(reddit.user.me())

	return reddit 

# To retrieve a number of latest submissions with default limit
# The result would be return as a json object 
def retrieveSubmission(reddit, number=200):
	ss = list(reddit.subreddit(SUBREDDITS).new(limit=number))
	return ss

# Return a list of tuples [(s.created_utc, s.author.name)]
# This is used to filter out duplicate submission in the last retrieval span 
def last(slist):
	if len(slist) == 0:
		return []
	l = []
	max_utc = slist[0].created_utc
	for s in slist:
		if s.created_utc == max_utc:
			l.append((s.created_utc, s.id))
	return l

# Return a list of latest sumissions with duplicate ones filtered out 
def match(slist, last_submission):
	if len(last_submission) == 0:
		return []
	newlist = []
	for s in slist:
		if s.created_utc >= last_submission[0][0]:
			if (s.created_utc, s.id) not in last_submission:
				newlist.append(s)
	return newlist

def updateOnce(reddit, last_submission):
	rawlist = retrieveSubmission(reddit, NUMTORETRIEVE)
	newlist = match(rawlist, last_submission)
	return (newlist)

def output(slist):
	if len(slist) == 0:
		return 
	filtered = []
	for s in slist:
		obj = dict()
		obj["id"] = s.id
		obj["created_utc"] = s.created_utc
		obj["subreddit"] = s.subreddit.display_name
		obj["author"] = s.author.name
		obj["url"] = s.url
		filtered.append(obj)
	jfile = json.dumps(filtered)
	# fname = str(int(last(slist)[0][0])) + ".json"
	# with open(fname, "w") as f:
	# 	f.write(jfile)

	return filtered

def printSubmission(slist):
	if len(slist) == 0: return
	for s in slist:
		obj = dict()
		obj["id"] = s.id
		obj["created_utc"] = s.created_utc
		obj["subreddit"] = s.subreddit.display_name
		obj["author"] = s.author.name
		# obj["url"] = s.url
		print(obj)

def showPrawRes():
	reddit = login()
	print("Round 1")
	firstlist = retrieveSubmission(reddit, NUMTORETRIEVE)
	last_sub = last(firstlist)
	if PRODUCTION == 0: printSubmission(firstlist)
	else: output(firstlist)
	print("Submission number:", len(firstlist))
	print("The file name should be:", last(firstlist)[0][0])

	listJson = output(firstlist)

	# for i in range(TIMES-1): 
	# 	time.sleep(SLEEPTIME)
	# 	print("Round", i+2)
	# 	newlist = updateOnce(reddit, last_sub)
	# 	if PRODUCTION == 0: printSubmission(newlist)
	# 	else: output(newlist)
	# 	if len(newlist) != 0:
	# 		last_sub = last(newlist)
	# 		print("Submission number:", len(newlist))
	# 		print("The file name should be:", last(newlist)[0][0])
	# 	else:
	# 		print("Submission number: 0")
	# 		print("No file output")

	print('Final Response:')
	print(listJson)
	return listJson