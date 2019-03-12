import prawUpdate as pu
import databaseUpdate as du
import time
import json
from pymongo import MongoClient

"""
This is the main program to run

Note: You may have to install PRAW and PyMongo beforehand
>> pip install praw
>> pip install pymongo

Note: For user GUI of MongoDB, you are recommended to install Robo 3T Community

Shen Pei-min, March 4, 2019
"""
def showPrawRes():
    TIMES = 1
    SLEEPTIME = 20
    NUMTORETRIEVE = 50
    SUBREDDITS = "news+worldnews"
    DATABASE = "mongodb://admin:iimt4601@ds019481.mlab.com:19481/iimt4601"
    DOMAINDB = 'testDomains_1'
    USERDB = 'testUsers_1'
    
    reddit = pu.login()
    print("Round 1")
    firstlist = pu.retrieveSubmission(reddit, NUMTORETRIEVE)
    last_sub = pu.last(firstlist)
    
    with MongoClient(DATABASE) as client:
        db = client.iimt4601
        domaincoll = db[DOMAINDB]
        usercoll = db[USERDB]
    
        # update database
        inp = pu.tojson(firstlist)
        start_time = time.time()
        update = du.parseSubmission(json.loads(inp))
        print(du.bulkUpdate(domaincoll, usercoll, update))
        interval = time.time() - start_time
        print("### The update takes", interval, "seconds ###")
        print("New submission number:", len(firstlist))

        for i in range(TIMES-1): 
            if (SLEEPTIME - interval) >= 0:
                time.sleep(SLEEPTIME - interval)
            print("Round", i+2)
            newlist = pu.updateOnce(reddit, last_sub)
        
            if len(newlist) != 0:
                # update database
                inp = pu.tojson(newlist) 
                start_time = time.time()
                update = du.parseSubmission(json.loads(inp))
                print(du.bulkUpdate(domaincoll, usercoll, update))
                interval = time.time() - start_time
                print("### The update takes", interval, "seconds ###")
                print("Current time:", time.time())
                print("New submission number:", len(newlist))
                last_sub = pu.last(newlist)
            else:
                print("Current time:", time.time())
                print("New submission number: 0")
                print("No update to database")
        return usercoll.find()
