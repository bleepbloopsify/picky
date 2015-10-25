import sqlite3
import hashlib
import oauth2
import argparse
import json
import urllib
import urllib2
import datetime

#SQLITE STUFF
def create():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    createlogin = "CREATE TABLE IF NOT EXISTS login (username text, password text)"
    c.execute(createlogin)

    createinfo = "CREATE TABLE IF NOT EXISTS info (username text, restaurant text, location text, rating real, day text, category text)"
    c.execute(createinfo)
    conn.commit()

def newUser(username, password):
    conn = sqlite3.connect("database.db")
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
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    m = hashlib.sha224(password).hexdigest()
    query = "SELECT password FROM login WHERE username=\"%s\"" % (username)
    c.execute(query)
    userdata = c.fetchone()[0]
    if userdata == None:
        return "Cannot find Username"
    if m == userdata:
        userstore = username
        return ""
    return "Incorrect Password"

def setrating(uname, rating, location, restaurant, category):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    query = "INSERT INTO info VALUES (\"%(username)s\", \"%(restaurant)s\", \"%(location)s\", \"%(rating)f\", \"%(day)s\", \"%(category)s\")"%({
    "username":uname,"restaurant":restaurant,"location":location, "rating":rating,"day":datetime.date.today(), "category":category})
    c.execute(query)
    conn.commit()

def getrating(location, restaurant):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    query = "SELECT rating FROM info WHERE restaurant=:rest AND location=:loc"
    data = c.execute(query, {"rest":restaurant, "loc":location}).fetchall()
    data = [f[0] for f in data]
    conn.commit()
    return data

def getUserCategories(uname):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    query = "SELECT category FROM info WHERE username=:uname"
    data = c.execute(query, {"uname":uname}).fetchall()
    cats = {}
    for d in [d[0] for d in data]:
        cats[d] += 1
    conn.commit()
    return data

#def record_restaurant():
#API STUFF
API_HOST = 'api.yelp.com'
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 3
SEARCH_PATH = '/v2/search/'
#BUSINESS_PATH = '/v2/business/'

# OAuth credential placeholders that must be filled in by users.
CONSUMER_KEY = "LsCXQQuggKugyyJCt4DkDw"
CONSUMER_SECRET = "TG8tyKlYvMTG3zSfn-YBNCOuuSk"
TOKEN = "B2wxvqBxgXYZ8tZWMBn4QU5Sm01MVeUN"
TOKEN_SECRET = "RL8NahsPX5xNXCE3aHM-y9iqYj4"

def request(url_params=None,host=API_HOST, path=SEARCH_PATH):
    """Prepares OAuth authentication and sends the request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        urllib2.HTTPError: An error occurs from the HTTP request.
    """

    url_params = url_params or {}
    url = 'https://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_request = oauth2.Request(method="GET", url=url, parameters=url_params)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()

    print u'Querying {0} ...'.format(url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response

def getTypes(addr,rad=8000):
    url_params = {
    'term':'restaurants',
    'location':addr.replace(' ','+'),
    'radius':rad,
    }
    raw = request(url_params)
    types = []
    for business in raw['businesses']:
        for category in business['categories']:
            if category[0] not in types:
                types += [category[0]]
    return types

def filter(addr, rad=8000, types="bars"):
    print "ok!"
    url_params = {
        'term':'restaurants',
        'location':addr.replace(' ','+'),
        'category_filter':types,
        'radius':rad,
        'limit':5
    }
    print "Ok!"
    raw = request(url_params)
    restaurants = []
    for business in raw['businesses']:
        restaurants += [{
            'name':business['name'],
            'location':business['location']['display_address'],
            'category':business['category_filter'],
            'rating':business['rating'],
            'distance':str(business['distance'])[:str(business['distance']).find('.')+1] + 'm'
        }]
        print "ok!"
    return restaurants
