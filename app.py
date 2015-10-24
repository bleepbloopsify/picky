from flask import Flask, render_template, request, session, redirect, url_for
import util

app = Flask(__name__)
app.secret_key = "nothing"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods = ["GET","POST"] )
def login():
    if request.method == "POST":
        form = request.form
        username = form.get('user')
        password = form.get('pwd')
        auth = util.authenticate(username, password)
        if auth == "":
            session['user'] = username
            return redirect('/')
        else:
            return render_template('login.html', err=auth)
    return render_template('login.html')

@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == "POST":
        form = request.form
        user = form.get('user')
        pwd = form.get('pwd')
        pwdtwo = form.get('pwd2')
        if pwd != pwdtwo:
            return render_template('register.html')
        util.new_user(user,pwd)
    return render_template('register.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
