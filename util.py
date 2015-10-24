import sqlite3
import hashlib
import oauth2
import argparse
import json
import urllib
import urllib2

#SQLITE STUFF
def create():
    conn = sqlite3.connect("login.db")
    c = conn.cursor()
    create = "CREATE TABLE login (username text, passwosd text)"
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
    print url
    
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



def filter(rad, types="bars",addr="345 Chambers Street"):
    url_params = {
        'location':addr.replace(' ','+'),
        'category_filter':types,
        'radius':rad,
        'limit':5
    }
    print request(url_params)
    return request(url_params)
