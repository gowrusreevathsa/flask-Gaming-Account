from flask import Flask, render_template, request, redirect, url_for, session
from bson import ObjectId
from pymongo import MongoClient    
from flask_socketio import SocketIO, send, emit
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Some random secret key that is pretty hard to crack'
socketio = SocketIO(app, cors_allowed_origins = '*')

@app.route('/')
@app.route('/index/')
def index():
    return render_template('index.html')

@app.route('/signUp/')
def signUp():
    return render_template('signUp.html')

@app.route('/signUpData/', methods = ['POST'])
def signUpData():
    if request.method == 'POST':
        data = request.form
        if users.count_documents({"_id" : data['nickname']}, limit = 1):
            return render_template('signUp.html')
    
    print(data['type'])
    result = {
            "_id" : data['nickname'],
            "fname" : data['fname'],
            "lname" : data['lname'],
            "phNum" : data['phNum'],
            "email" : data['email'],
            "pass" : hashlib.sha256((data['fpass']).encode()).hexdigest(),
            "city" : data['city'],
            "country" : data['country'],
            "type" : data['type']
        }
    # for i in data:
    if data['type'] == 'gamer':
        res = users.insert_one(result)
    else:
        res = users.insert_one(result)
    print(res)
    return redirect(url_for('index'))

@app.route('/login/', methods = ['POST'])
def login():
    if request.method == 'POST':
        data = request.form
    else:
        return redirect(url_for('index'))
    return authLogin(data)

def authLogin(data):
    usernameInp = data['usernameInp']
    passInp = data['passInp']
    if users.count_documents({"_id" : usernameInp}, limit = 1):
        for i in users.find({"_id": usernameInp}, limit = 1):
            if i['pass'] == hashlib.sha256(passInp.encode()).hexdigest():
                session['username'] = usernameInp
                session['type'] = 'user'
                return redirect(url_for('home'))
    else:
        return redirect(url_for('index'))

@app.route('/home/')
def home():
    return render_template('home.html')

@app.route('/storeGameData/')
def storeGameData():
    return render_template('GameData.html')

@socketio.on('gameData')
def handle_gameData(msg):
    print(msg)
    if users.count_documents({"_id" : msg['username']}, limit = 1):
        game = db[session['gamename']]
        data = [{
            "_id" : msg['username'],
            "par1" : msg['par1'],
            "par2" : msg['par2'],
            "par3" : msg['par3']
        }]
        if game.count_documents({"_id" : msg['username']}, limit = 1):
            game.update_one({"_id" : msg['username']}, {'$set' : data})
        else:
            game.insert_one(data)

        #After insert/update
        for i in game.find_one({"_id" : msg['username']}):
            print(i)
    else:
        print("User not registered to Gaming Account")
        return render_template('GameData.html')
    # for i in msg:

@socketio.on('loginAsGameSocket')
def handle_loginAsGameSocket(msg):
    # for data in msg:
    usernameInp = msg['username']
    passInp = msg['pass']
    print(usernameInp + ' ' + passInp)
    if users.count_documents({"_id" : usernameInp}, limit = 1):
        print("In IF")
        for i in users.find({"_id": usernameInp}, limit = 1):
            print("In IF")
            if i['pass'] == hashlib.sha256(passInp.encode()).hexdigest():
                print("In IF")
                session['gamename'] = usernameInp
                session['type'] = 'game'
                emit('redirect', {'url' : url_for('storeGameData')})

if __name__ == '__main__':
    client = MongoClient("mongodb://127.0.0.1:27017")
    db = client['GamingAccount']
    users = db['users']
    games = db['games']
    socketio.run(app, debug = True)