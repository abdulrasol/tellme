from flask import Flask, render_template, session, redirect, request
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import helpers, os, sqlite3


app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['UPLOAD_FOLDER'] = helpers.UPLOAD_DIR
app.config['USERS_UPLOADS'] = helpers.USER_PROFILE_PIC



@app.route('/')
def home(msg=None):
    if session.get("user"):
       db = sqlite3.connect('database.db')
       db.row_factory = helpers.dict_factory
       c = db.cursor()
       user = c.execute('SELECT * FROM users WHERE username = ?', (session.get('user'), )).fetchall()[0]
       db.close()
       return render_template('profile.html', msg=msg, profile=True, user=user)
    return render_template('home.html', home=True, msg=msg)

@app.route('/<username>')
def user(username, msg=None):
    db = sqlite3.connect('database.db')
    db.row_factory = helpers.dict_factory
    c = db.cursor()
    try:
        user = c.execute("SELECT username, name, email, bio, picture, short FROM users WHERE username = ?", (username, )).fetchall()[0]
        return render_template('user.html', msg=msg, user=user)
    except Exception:
        return render_template('404.html',msg=msg)
    finally:
        db.close()
    
    
# logout function
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        # connect to db
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        # chech username
        if cursor.execute("SELECT count(id) FROM users WHERE username=?", (request.form.get('username'),)).fetchall()[0][0] != 0:
            return home(msg={'text':'should trying anothor one','title':'username was taken!','type':'warning'})
        # check email
        if cursor.execute("SELECT count(id) FROM users WHERE email=?", (request.form.get('email'),)).fetchall()[0][0] != 0:
            return home(msg={'title':'Email was registerd, log in or','text':'should trying anothor one','type':'warning'})
        # check password
        if request.form.get('password1') != request.form.get('password2'):
            return home(msg={'text':'passwords doesn\'t match!','title':'Error','type':'danger'})
        user = (request.form.get('username'), request.form.get('email'), generate_password_hash(request.form.get('password1')),)
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", user)
        db.commit()
        db.close()

        session['user'] = request.form.get('username')
        session['user_auth'] = True

    return home(msg={
        "text": "You are registered!",
        "title": "Welcome",
        "type": "primary"
    })

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
    
        # connect to db
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        c = cursor.execute("SELECT username, password FROM users WHERE username = ?", ( request.form.get('username'), )).fetchall()
        if len(c) == 0:
            return home({"text": "does not match!", "title": "Username", "type": "danger"})
        if request.form.get('username') == c[0][0] and  check_password_hash(c[0][1], request.form.get('password')):
            session['user'] = c[0][0]
            return home()
        else:
            return home({"text": "does not match!", "title": "Password", "type": "danger"})
    return home({"text": "Enter username and password", "title": "", "type": "warning"}) 

@app.route('/profile', methods=["GET", "POST"])
def edit_profile():
    if request.method == 'POST':
        db = sqlite3.connect('database.db')
        c = db.cursor()
        if request.form.get('username'):
            c.execute("UPDATE users set username = ? where username = ?", (request.form.get('username'), session['user'],))
            session['user'] = request.form.get('username')
        if request.form.get('email'):
            c.execute("UPDATE users set email = ? where username = ?", (request.form.get('email'), session['user'],))
        if request.form.get('name'):
            c.execute("UPDATE users set name = ? where username = ?", (request.form.get('name'), session['user'],))
        if request.form.get('short'):
            c.execute("UPDATE users set short = ? where username = ?", (request.form.get('short'), session['user'],))
        if request.form.get('bio'):
            c.execute("UPDATE users set bio = ? where username = ?", (request.form.get('bio'), session['user'],))
        if request.form.get('password2') and request.form.get('password1'):
            old_pass = c.execute('SELECT password FROM users WHERE username = ?', (session['user'],)).fetchall()[0][0]
            if check_password_hash(old_pass, request.form.get('password1')):
                c.execute("UPDATE users set password = ? where username = ?", (generate_password_hash(request.form.get('password2')), session['user'],))
            else:
                return home({
                            "title": "Old Password",
                            "text": "Does not match",
                            "type": "warning"
                        })  
        if request.files.get('picture'):
            pic = request.files.get('picture')
            name = pic.filename.rsplit('.')[-1]
            pic.save(os.path.join(helpers.USER_PROFILE_PIC, session['user']+'.'+name))
            pic = f"static/uploads/users/{session['user']}.{name}"
            c.execute("UPDATE users set picture = ? where username = ?", (pic, session['user'],))
            
        db.commit()
        db.close()
        
        return home({
            "title": "Profile",
            "text": "updates",
            "type": "success"
        })
    return home()

msg = {
        "text": "Google it",
        "title": "test",
        "type": "primary"
    }

