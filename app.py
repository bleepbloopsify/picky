from flask import Flask, render_template
import util

app = Flask(__name__)
app.secret_key = "nothing"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

if __name__ = '__main__':
    app.debug = True
    app.run()
