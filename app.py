from flask import Flask, render_template, request, session, redirect, url_for, Response, jsonify
import util

app = Flask(__name__)
app.secret_key = "nothing"
util.create()

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/restaurants', methods=["GET","POST"])
def restaurants():
    if 'user' not in session:
        return redirect('/login')
    if request.method == "POST":
        form = request.form
        print form
        details = form['details']
        details = details.strip().strip(',').split(';')
        #address radius ratings categories
        address = details[0]
        radius = int(details[1]) * 1609
        rating = details[2]
        types = details[3].split(',')

        session['addr'] = address
        results = util.filter(address,radius,types,rating)
        return render_template('restaurants.html', results=results,suggest=util.suggest(session['user'],results))
    return redirect('/index')

@app.route('/results')
def results():
     args = request.args
     addr = args.get('addr')
     result = util.getTypes(addr)
     return jsonify(result=result)

@app.route('/history')
@app.route('/history/<location>/<restaurant>/<category>', methods=['GET','POST'])
def history(location="",restaurant="",category=""):
    if location=="":
        return redirect('/index')
    if request.method == "POST":
        form = request.form
        rating = form['rating']
        util.setrating(session['user'], rating, location, restaurant, category)
    rating = util.getrating(location)
    if len(rating) > 0:
        rating = reduce(lambda x, y: x+y, rating)/len(rating)
        rating = int(rating * 10)  / 10.
    else:
        return render_template('rating.html',rating = "NO USER RATING")
    return render_template('rating.html',rating = rating)

@app.route('/login', methods = ["GET","POST"] )
def login():
    if request.method == "POST":
        form = request.form
        username = form.get('user')
        password = form.get('pwd')
        auth = util.authenticate(username, password)
        print auth
        if auth == "":
            session['user'] = username
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
  return render_template("/about.html")


if __name__ == '__main__':
    app.debug = True
    app.run(host = "0.0.0.0", port = 8080)
