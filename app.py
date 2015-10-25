from flask import Flask, render_template, request, session, redirect, url_for, Response, jsonify
import util
import hashlib
import random

app = Flask(__name__)
app.secret_key = "nothing"
util.create()

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/restaurants', methods=["GET","POST"])
def restaurants():
    if request.method == "POST":
        form = request.form
        details = form['details']
        details = [c.strip() for c in details.strip().strip(',').split(';')]
        #address radius ratings categories
        address = details[0]
        radius = int(details[1]) * 1609
        rating = details[2]
        types = [d.strip() for d in details[3].split(',')]
        session['setrad'] = details[1]
        session['setrating'] = rating
        session['addr'] = address
        results = util.filter(address,radius,types,rating)

        for result in results:
            result['category'] = catformat(result['category'])
        return render_template('restaurants.html', results=results,categories=util.getTypes(address,radius))
    return redirect('/index')

def catformat(cats):
    dog = ""
    for cat in cats:
        dog += cat + ","
    return dog[:-1]

@app.route('/results')
def results():
     args = request.args
     addr = args.get('addr')
     result = util.getTypes(addr)
     return jsonify(result=result)

@app.route('/history')
@app.route('/history/<location>/<restaurant>/<category>/<rating>', methods=['GET','POST'])
def history(location="",restaurant="",category="",rating=0):
    if location=="":
        return redirect('/index')
    # if request.method == "POST":
    #     form = request.form
    #     rating = form['rating']
    #     session['rating'] = rating
    #     util.setrating(session['user'], rating, location, restaurant, category)
    #rating = util.getrating(location)
    session['rating'] = int(rating.strip('?'))
    # if len(rating) > 0:
    #     rating = reduce(lambda x, y: x+y, rating)/len(rating)
    #     rating = int(rating * 10)  / 10.
    #else:
    #damn = util.filter(location.split(',')[0] + " " + location.split(',')[1], 10000)
    #print damn
    #damn = damn[random.randrange(len(damn))]
    #damn = '/restaurant/%s,%s,%s/%s/%s/%s'%(damn['location'][0],damn['location'][1],damn['location'][2],damn['name'],catformat(damn['category']),damn['rating'])
    return render_template('rating.html',restaurant=restaurant,location=location.split(','),category=category.split(','))
    #return render_template('rating.html',rating = rating,restaurant=restaurant,location=location.split(','),category=category.split(','))

@app.route('/login', methods = ["GET","POST"] )
def login():
    if request.method == "POST":
        form = request.form
        username = form.get('user')
        password = form.get('pwd')
        auth = util.authenticate(username, password)
        if auth == "":
            session['user'] = username
            session['userhash'] = m = hashlib.sha224(username).hexdigest()
            return redirect('/')
        else:
            return render_template('login.html', error=auth)
    return render_template('login.html')

@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == "POST":
        form = request.form
        user = form.get('user')
        pwd = form.get('pwd')
        pwdtwo = form.get('pwd2')
        if pwd != pwdtwo:
            return render_template('register.html',err="Passwords Do Not Match")
        elif len(pwd) < 6:
            return render_template('register.html', err="Password must be at least 6 characters")
        elif not pwd.isalnum():
            return render_template('register.html', err="Password cannot contain special characters")
        elif not util.newUser(user,pwd):
            return render_template('register.html', err="Username Taken")
        else:
            session['user'] = user
            return redirect('/index')
    return render_template('register.html')

@app.route("/address")
def address():
  return render_template("/address.html")

@app.route("/about")
def about():
    about = ""
    with open("README.txt") as file:
        about = file.read()
    return render_template("/about.html",about=about)


if __name__ == '__main__':
    app.debug = True
    app.run(host = "0.0.0.0", port = 8080)
