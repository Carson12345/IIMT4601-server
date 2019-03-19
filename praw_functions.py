from pymongo import MongoClient

"""
This is a function specifically implemented for server to call. 
For the actual update mechanism, please see streamUpdate.py.

rebpm, March 19, 2019
"""
def showPrawRes():
    DATABASE = "mongodb://admin:iimt4601@ds019481.mlab.com:19481/iimt4601"
    USERDB = 'testUsers_1'
    
    with MongoClient(DATABASE) as client:
        db = client.iimt4601
        usercoll = db[USERDB]
        return usercoll.find({'score':{'$gt':0.4}})
