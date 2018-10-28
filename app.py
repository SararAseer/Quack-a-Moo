'''
Quack-a-Moo
Mohammed S. Jamil, Isaac Jon, Ahnaf Kazi, Addison Huang
SoftDev1 pd6
P #00: Da Art of Storytellin'
2018-10-01
'''
from flask import Flask,render_template,request,session,url_for,redirect,flash
from os import urandom
from util import db_updater as update
from passlib.hash import sha256_crypt

import sqlite3 #imports sqlite
DB_FILE="data/quackamoo.db"
db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
c = db.cursor() #facilitates db operations

app = Flask(__name__)
app.secret_key = urandom(32)

@app.route("/")
def home():
    if "logoutbutton" in request.args:
        session.pop('username')
    if 'username' in session:
        username = session['username']
        DB_FILE="data/quackamoo.db"
        db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
        c = db.cursor()
        command = 'SELECT storyId,title FROM logs WHERE logs.username = "{0}";'.format(username)
        c.execute(command)
        editedList = c.fetchall()
        temp = []
        command = 'SELECT storyId,title FROM logs ORDER BY entryId;'
        c.execute(command)
        most = []
        temp = c.fetchall()
        most.append(temp[0])
        prev = temp[0][0]
        print("\n\n\n\n\n\n\n\n")
        for story in temp:
            print(story[0])
            if story[0] != prev:
                print(story[0])
                most.append(story)
        return render_template('home.html',edited=editedList, popular=most)
    else:
        return render_template('auth.html')

@app.route("/auth",methods=['GET','POST'])
def authPage():
    DB_FILE="data/quackamoo.db"
    db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
    c = db.cursor() 
    username=request.form['username']
    command = 'SELECT password FROM users WHERE users.username = "{0}"'.format(username)
    c.execute(command)
    password = c.fetchone()#gets the password for the user if the user is in db
    print(password)
    if password == None:
        flash('incorrect credentials')
        return redirect(url_for('home'))
    elif sha256_crypt.verify(request.form['password'], password[0]):
        session['username'] = username
        #these lists contain titles of stories on our homepage
        DB_FILE="data/quackamoo.db"
        db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
        c = db.cursor()
        command = 'SELECT storyId,title FROM logs WHERE logs.username = "{0}";'.format(username)
        c.execute(command)
        editedList = c.fetchall()
        
        temp = []
        command = 'SELECT storyId,title FROM logs ORDER BY entryId;'
        c.execute(command)
        most = []
        temp = c.fetchall()
        most.append(temp[0])
        prev = temp[0][0]
        print("\n\n\n\n\n\n\n\n")
        for story in temp:
            print(story[0])
            if story[0] != prev:
                print(story[0])
                most.append(story)
                prev = story[0]
        return render_template('home.html',edited=editedList, popular=most)
    else:
        flash('incorrect credentials')
        return redirect(url_for('home'))
@app.route("/reg",methods=['GET','POST'])
def reg():
    return render_template('reg.html')
@app.route("/added",methods=['GET','POST'])
def added():
    DB_FILE="data/quackamoo.db"
    newUsername = request.form['username']
    newPassword = sha256_crypt.encrypt(request.form['password'])
    db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
    c = db.cursor() 
    command = 'SELECT username FROM users WHERE users.username = "{0}";'.format(newUsername)
    c.execute(command)
    userList = c.fetchall()
    print(userList)
    if userList == [] :
        insert = "INSERT INTO users VALUES(?,?)"
        params=(newUsername,newPassword)
        c.execute(insert,params)
        db.commit()
        db.close()
        #session['username'] = newUsername
        return redirect(url_for('home'))
    else:
        flash('Username Taken')
        return redirect(url_for('reg'))


#@app.route("/logout")
#def logout():
#   if 'username' in session:
#        session.pop('username')
#    return redirect(url_for("home"))
@app.route("/all")
def all():
    DB_FILE="data/quackamoo.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    getstories="SELECT title,storyId FROM stories"
    c.execute(getstories)
    storylist=c.fetchall()
    if 'username' in session:
        return render_template('all.html',storylist=storylist)
    else:
        return redirect(url_for("home"))
@app.route("/create",methods=['GET','POST'])
def create():
    if 'username' in session:
        return render_template('create.html')
    else:
        return redirect(url_for("home"))
    
@app.route("/view",methods=['GET','POST'])
def view():
    if 'username' in session:
        #variables for code readability
        username = session["username"]
        if request.referrer == "http://127.0.0.1:5000/create":
            title = request.form["title"]
            body = request.form["body"]
            update.create(title, body, username)
        else:
            title = request.args["title"]
            storyId= request.args["storyId"] 
            if "submit" in request.form:
                body=request.form["body"]
                update.add(title,body,username,storyId) 
            DB_FILE="data/quackamoo.db"
            db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
            c = db.cursor() 
            print(title,storyId)
            command = 'SELECT body FROM stories WHERE stories.title = "{0}" AND stories.storyId ="{1}";'.format(title,storyId)
            c.execute(command)
            body=c.fetchone()[0]
            print(body)
        return render_template('view.html',title=title, story=body)
    else:
        return redirect(url_for("home"))
    
@app.route("/edit",methods=['GET','POST'])
def edit():
    if 'username' in session:
        DB_FILE="data/quackamoo.db"
        title=request.args["title"]
        storyId = request.args["storyId"]
        db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
        c = db.cursor() 
        username = session["username"]
        check="SELECT storyId FROM logs WHERE username = (?) AND storyId=(?);"
        c.execute(check,(username,storyId))
        edited=c.fetchone()#this variable is used to check if a user has edited a story, if its empty the user has not edited it
        print(edited)
        if edited != None :
           flash("Already edited view from home page")
           return redirect(url_for("home")) 
        c.execute("SELECT entryId FROM logs") #selects all of the entryids
        entryIds = c.fetchall()
        print(entryIds)
        last=entryIds[len(entryIds)-1][0]
        command = 'SELECT body FROM logs WHERE logs.title = "{0}" AND logs.entryId= {1};'.format(title,last)
        c.execute(command)
        body=c.fetchone()[0]
        print(body)
        print(title)
        return render_template('edit.html',title=title, story=body, storyId = storyId)
    else:
        return redirect(url_for("home"))
if __name__ == '__main__':
        app.debug = True
        app.run()
