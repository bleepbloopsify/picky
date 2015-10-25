from flask import Flask, render_template, request, session, redirect, url_for
import util

app = Flask(__name__)
app.secret_key = "nothing"
util.create()

@app.route('/')
@app.route('/index', methods=['GET','POST'])
def index():
    return render_template('index.html')


@app.route('/history')
@app.route('/history/<location>', methods=['GET','POST'])
def history(location=""):
    if location=="":
        return redirect('/')

    rating = util.getrating(location)
    rating = reduce(lambda x, y: x+y, rating)/len(rating)
    rating = int(rating * 10)  / 10.
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
        if not util.newUser(user,pwd):
            return render_template('register.html', err="Username Taken")
        else:
            session['user'] = user
            return redirect('index.html')
    return render_template('register.html')

@app.route("/address")
def address():
  return render_template("/address.html")

if __name__ == '__main__':
    app.debug = True
    app.run()
