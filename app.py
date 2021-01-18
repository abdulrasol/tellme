from flask import Flask, render_template, session, redirect
from flask_session import Session
from tempfile import mkdtemp

app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def home(msg=None):
    session.clear()
    
    return render_template('home.html', home=True, msg=msg)

@app.route('/<username>')
def user(username, msg=None):
    return render_template('profile.html', msg=msg)

@app.route('/profile')
def profile():
    session['user'] = 'rasol'
    return render_template('profile.html', profile=True)

# logout function
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

msg = {
        "text": "Google it",
        "title": "test",
        "type": "primary"
    }