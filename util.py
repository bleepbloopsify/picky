import sqlite3
import hashlib
import requests
import oauth2
import argparse
import json
import urllib
import urllib2

#SQLITE STUFF
def create():
    conn = sqlite3.connect("login.db")
    c = conn.cursor()
    create = "CREATE TABLE login (username text, password text)"
    c.execute(create)



def newUser(username, password):
    conn = sqlite3.connect("login.db")
    c = conn.cursor()
    c.execute("SELECT username FROM login WHERE username=:uname LIMIT 1", {"uname":username})
    data = c.fetchone()
    if data is None :
        m = hashlib.sha224(password)
        query = "INSERT INTO login VALUES (\"%(username)s\", \"%(password)s\")" % ({"username":username, "password":m.hexdigest()})
        c.execute(query)
        conn.commit()
        return True
    return False

def authenticate(username, password):
    conn = sqlite3.connect("login.db")
    c = conn.cursor()
    m = hashlib.sha224(password).hexdigest()
    query = "SELECT password FROM login WHERE username=\"%s\"" % (username)
    c.execute(query)
    userdata = c.fetchone()
    if userdata == None:
        return "Cannot find Username"
    if m == userdata['password']:
        userstore = username
        return ""
    return "Incorrect Password"

#def record_restaurant():

def pull(addr, typ, rad):
    API_HOST = 'api.yelp.com'
    DEFAULT_TERM = 'dinner'
    DEFAULT_LOCATION = 'San Francisco, CA'
    SEARCH_LIMIT = 3
    SEARCH_PATH = '/v2/search/'
    BUSINESS_PATH = '/v2/business/'

# OAuth credential placeholders that must be filled in by users.
    CONSUMER_KEY = None
    CONSUMER_SECRET = None
    TOKEN = None
    TOKEN_SECRET = None
    uri = "https://api.yelp.com/v2/search?term=food&sort=1%(address)s%(types)s%(radius)s"

    client = oauthlib.auth1.Client('LsCXQQuggKugyyJCt4DkDw',client_secret='TG8tyKlYvMTG3zSfn-YBNCOuuSk')
    uri, headers, body = client.sign('https://')

    address = "&location=%s"%(addr)
    types = "&category_filter=%s"%(typ)
    radius = "&radius_filter=%s"%(rad)
    r = requests.get(url%(app_key,))
    return ""

def filter():
    return ["mcd"]
