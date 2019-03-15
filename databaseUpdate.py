from pymongo import MongoClient, ReturnDocument
import urlparse
import pandas as pd
import json
import time 
import sys

sampleuser = {"author":"tigris986","very_high":3,"high":3,"mixed":5, "low":1, "very_low":0, "none":8,"count":20,"score":0.0875}
samplesub = {"url":"usanewstoday.org", "author":"user2"}
samplesubs = [
    {"url":"mercatus.org", "author":"user1"}, 
    {"url":"nationalacademyofsciences.org", "author":"user6"}, 
    {"url":"ourhealthguides.com", "author":"user3"}, 
    {"url":"thenewtropic.com", "author":"user7"}
]
tagDict = {
    "VeryHigh":"very_high", 
    "High":"high",
    "Mixed":"mixed", 
    "Low":"low",
    "VeryLow":"very_low", 
    "None":"none",
    "Score":"score"
}
spam = [
    {'id': 'ax57pu', 'created_utc': 1551691375.0, 'subreddit': 'worldnews', 'author': 'internalocean', 'url': 'https://www.reuters.com/article/us-india-kashmir-pakistan-airports/pakistan-adds-flights-delays-reopening-of-commercial-airspace-idUSKCN1QL0SH?feedType=RSS&feedName=worldNews&utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+Reuters%2FworldNews+%28Reuters+World+News%29'},
    {'id': 'ax56di', 'created_utc': 1551691063.0, 'subreddit': 'worldnews', 'author': 'LineNoise', 'url': 'https://www.theguardian.com/uk-news/2019/mar/04/unusual-activity-russian-embassy-novichok-attack-skripal-poisonings'},
    {'id': 'ax569x', 'created_utc': 1551691038.0, 'subreddit': 'worldnews', 'author': 'man_of_extremes', 'url': 'https://economictimes.indiatimes.com/news/defence/india-russia-to-ink-3-billion-nuclear-submarine-deal-this-week/articleshow/68248638.cms?utm_source=twitter.com&utm_medium=Social&utm_campaign=ETTWMain'},
    {'id': 'ax53u1', 'created_utc': 1551690474.0, 'subreddit': 'worldnews', 'author': 'internalocean', 'url': 'https://www.reuters.com/article/us-kenya-crash/helicopter-crash-kills-four-americans-and-their-pilot-in-kenya-idUSKCN1QL0GJ?feedType=RSS&feedName=worldNews&utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+Reuters%2FworldNews+%28Reuters+World+News%29'}
]

def insertNewAuthor(usercoll, author):
    authorObj = {"author":author,"very_high":0,"high":0,"mixed":0, "low":0, "very_low":0, "none":0,"count":0,"score":0}
    usercoll.insert_one(authorObj)
    print("Insert successful!")

def multiDomains(coll):
    domains = ['21stcenturywire.com', 'fas.org', 'personalliberty.com']
    # cursor object is essentially a list of SON object that can be treated as dict 
    doc = coll.find({'Domain':{'$in':domains}})
    for d in doc:
        print(d)

# sub = {"url":submissionUrl, "author":submissionAuthor}
# got to handle new author 
def singleUpdate(domaincoll, usercoll, sub):
    try:
        expression = '.*'+sub['url']+'.*'
        doc = domaincoll.find({'Domain':{'$regex':expression}})[0] 
    except IndexError as err:
        return "Error in domain query: "+str(err)+" when querying for "+sub['url']

    try:
        user = usercoll.find({'author':sub['author']})[0]
    except IndexError:
        print("Insert new author", sub['author'],"to the user database")
        insertNewAuthor(usercoll, sub['author'])
        user = usercoll.find({'author':sub['author']})[0]

    # must update score before update count
    newscore = (user['score'] * user['count'] + doc['Score']) / (user['count'] + 1)
    usercoll.find_one_and_update({'author':sub['author']}, {'$inc':{tagDict[doc['Tag']]:1, 'count':1}, '$set':{'score':newscore}}, return_document=ReturnDocument.AFTER)
    return "Update: "+user['author']

def bulkUpdate(domaincoll, usercoll, submissions):
    for sub in submissions:
        print(singleUpdate(domaincoll, usercoll, sub))
    return "Bulk update finished."

def parseSubmission(submissions):
    """
    Return submissions with only author and url fields
    input: 'id':'created_utc':'subreddit':'author':'url'
    """
    parsed = []
    for s in submissions:
        obj = dict()
        obj['author'] = s['author']
        obj['url'] = parseUrl(s['url'])
        parsed.append(obj)
    return parsed

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


if __name__ == "__main__":
    with MongoClient("mongodb://admin:iimt4601@ds019481.mlab.com:19481/iimt4601") as client:
        db = client.iimt4601
        domaincoll = db['testDomains_1']
        usercoll = db['testUsers_1']
        fname = sys.argv[1]
        with open(fname,'r') as f:
            raw = json.loads(f.read())
            start_time = time.time()
            update = parseSubmission(raw)
            print(bulkUpdate(domaincoll, usercoll, update))
            print("The operation takes", time.time() - start_time, "seconds.")