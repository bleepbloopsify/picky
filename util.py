import pymongo
from pymongo import MongoClient
import hashlib


client = MongoClient()
db = client['database']

userlist = db.users


def new_user(user,pwd):
    m = hashlib.sha224(pwd)
    password = m.hexdigest()
    newuser = {"username":user, "pass":password }
    post_id = userlist.insert_one(newuser).inserted_id

def authenticate(user, pwd):
    m = sha224.new()
    m.update(pwd)
    password = m.hexdigest()
    if (userlist.find_one({"username":user}) == None):
        return "error"

#def record_restaurant():

def pull():
    return ""

def filter():
    return ["mcd"]
