import sqlite3
import hashlib
import oauth2
import argparse
import json
import urllib
import urllib2
import datetime
import operator
import random

#SQLITE STUFF
type_dist = {
    "Chinese":[
        "chinese", "hot pot", "shanghainese", "dim sum"
    ],
    "Japanese":[
        "sushi", "live/raw food", "teppanyaki", "japanese", "sushi bars"
    ],
    "Diner":[
        "sandwiches", "american", "diner", "deli", "hot dogs", "burgers", "southern", "breakfast", "fast food"
    ],
    "Middle Eastern":[
        "falafel", "egyptian", "afghan", "persian/iranian", "middle eastern"
    ],
    "Indian":[
        "bangladeshi", "pakistani", "indian"
    ],
    "Steakhouse":[
        "steakhouse"
    ],
    "Buffet":[
        "buffet"
    ],
    "Vegan":[
        "vegetarian", "vegan", "gluten free"
    ],
    "Mexican":[
        "mexican", "texmex"
    ],
    "Pizza":[
        "pizza","italian"
    ]
}

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
    userdata = c.fetchone()
    if userdata == None:
        return "Cannot find Username"
    userdata = userdata[0]
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

def getrating(location):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    query = "SELECT rating FROM info WHERE location=:loc"
    data = c.execute(query, { "loc":location}).fetchall()
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
YELP_HOST = 'api.yelp.com'
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 3
YELP_SEARCH_PATH = '/v2/search/'
#BUSINESS_PATH = '/v2/business/'

# OAuth credential placeholders that must be filled in by users.
CONSUMER_KEY = "LsCXQQuggKugyyJCt4DkDw"
CONSUMER_SECRET = "TG8tyKlYvMTG3zSfn-YBNCOuuSk"
TOKEN = "B2wxvqBxgXYZ8tZWMBn4QU5Sm01MVeUN"
TOKEN_SECRET = "RL8NahsPX5xNXCE3aHM-y9iqYj4"

def request(url_params=None,host=YELP_HOST, path=YELP_SEARCH_PATH):
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

    # if api == "google":
    #     CONSUMER_KEY = ""
    #     CONSUMER_SECRET ="NYHPtFCnNVhup9oVo9nDki9a"

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
    'radius':rad
    }
    raw = request(url_params)
    types = []
    for business in raw['businesses']:
        for category in business['categories']:
            added = 0
            for dist in type_dist:

                if category[0].lower() in type_dist[dist]:
                    if dist not in types:
                        types += [dist]
                    added = 1
            if category[0] not in types and added != 1:
                types += [category[0]]
    return types

def filter(addr, rad=8000, types=[], rating=0):
    url_params = {
        'term':'restaurants',
        'location':addr.replace(' ','+'),
        'radius':rad
    }
    raw = request(url_params)
    restaurants = []
    for business in raw['businesses']:
        restaurants += [{
            'name':business['name'],
            'location':business['location']['display_address'],
            'category':business['categories'],
            'rating':business['rating'],
            'distance':str(int((business['distance'] / 1609) * 100) / 100.) + 'mi',
            'link':business['url']
        }]
    for restaurant in restaurants:
        if float(restaurant['rating']) < float(rating):
            del restaurants[restaurant]
        else:
            restaurant['category'] = [c[0] for c in restaurant['category']]
            for category in restaurant['category']:
                if category in types:
                    del restaurants[restaurant]
                    break
    return restaurants


def suggest(uname, restaurants):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    query = "SELECT category FROM info WHERE username=:uname"
    data = c.execute(query, {"uname":uname}).fetchall()
    cats = {}
    for d in [d[0] for d in data]:
        for s in d.split(','):
            if s not in cats:
                cats[s] = 1
            else:
                cats[s] += 1
    fav = "helpme"
    most_visit = -1
    for k,v in cats.iteritems():
        if v > most_visit:
            fav = k
    a = random.randrange(99)
    choices = []
    if fav == "helpme":
        choices = [f['name'] for f in restaurants]
        return choices[random.randrange(len(choices))]
    elif a >= 0 and a < 30:
        for restaurant in restaurants:
            for  c in restaurant["category"]:
                if c == fav:
                    choices += [restaurant["name"]]
                    break
        return choices[random.randrange(len(choices))]
    elif a >= 30 and a < 85:
        for restaurant in restaurants:
            for  c in restaurant["category"]:
                if c != fav:
                    choices += [restaurant["name"]]
                    break
        return choices[random.randrange(len(choices))]
    else:
        for restaurant in restaurants:
            choices += [restaurant["name"]]
        return choices[random.randrange(len(choices))]
