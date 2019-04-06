import praw
import json
from pymongo import MongoClient, ReturnDocument
from urllib.parse import urlparse

SUBREDDITS = "news+worldnews+nottheonion+UpliftingNews+offbeat+gamernews+floridaman+energy+syriancivilwar+truecrime+Politics+worldpolitics+Libertarian+anarchism+socialism+conservative+politicalhumor+neutralpolitics+politicaldiscussion+ukpolitics+geopolitics+communism+completeanarchy"
DATABASE = "mongodb://admin:iimt4601@ds019481.mlab.com:19481/iimt4601"
DOMAINDB = 'testDomains_2'
USERDB = 'Users'

# "tag_in_domain_db":"data_field_in_user_db"
tagDict = {
    "Very High":"very_high", 
    "High":"high",
    "Mixed":"mixed", 
    "Low":"low",
    "Very Low":"very_low", 
    "None":"not_identified",
    "Score":"score"
}

def login(username='rebpm', password='NORI12onfire'):
	reddit = praw.Reddit(client_id='eG7xz4xynkS8hw',
                     	client_secret='ghMVADsKO9x0NN8szrgiOtWbrQ4',
                     	password=password,
                     	user_agent='testscript by /u/rebpm',
                     	username=username)
	return reddit 

def parseUrl(url):
    """
    Return only domain from each url
    input: https://www.reuters.com/path/to/some/ariticles
    return: reuters.com
    """
    mid = urlparse(url).netloc
    if 'www' in mid:
        if 'www1' in mid or 'www3' in mid:
            return mid
        else:
            domain = mid.split('.', 1)
            return domain[1]
    else:
        return mid

def insertNewAuthor(usercoll, author):
    authorObj = {"author":author,"very_high":0,"high":0,"mixed":0, "low":0, "very_low":0, "not_identified":0,"count":0,"score":0}
    usercoll.insert_one(authorObj)

def singleUpdate(domaincoll, usercoll, sub):

    try:
        user = usercoll.find({'author':sub['author']})[0]
    except IndexError:
        insertNewAuthor(usercoll, sub['author'])
        print("+ Inserted new author", sub['author'],"to the user database")
        user = usercoll.find({'author':sub['author']})[0]
    
    try:
        expression = '.*'+sub['url']+'.*'
        # print(expression)
        doc = domaincoll.find({'domain':{'$regex':expression}})[0] 
    except IndexError as err:
        usercoll.find_one_and_update({'author':sub['author']}, {'$inc':{tagDict['None']:1, 'count':1}}, return_document=ReturnDocument.AFTER)
        return "! Error in domain query: "+str(err)+" when querying for "+sub['url']+"\n* Update user's not_identified."

    try:
        # must update score before update count
        newscore = (user['score'] * user['count'] + doc['score']) / (user['count'] + 1 - user[tagDict['None']])
        usercoll.find_one_and_update({'author':sub['author']}, {'$inc':{tagDict[doc['tag']]:1, 'count':1}, '$set':{'score':newscore}}, return_document=ReturnDocument.AFTER)
        return "* Update: "+user['author']
    except KeyError:
        return "! KeyError when update_and_find user:"+sub['author']
    except TypeError:
        return "! TypeError when calculating new score for user: "+sub['author']+" for domain: "+sub['url']

if __name__ == "__main__":
    reddit = login()
    with MongoClient(DATABASE) as client:
        db = client.iimt4601
        domaincoll = db[DOMAINDB]
        usercoll = db[USERDB]
        reddit = login()
        for s in reddit.subreddit(SUBREDDITS).stream.submissions():
            obj = dict()
            obj["author"] = s.author.name
            obj["url"] = parseUrl(s.url)
            print(singleUpdate(domaincoll, usercoll, obj))
