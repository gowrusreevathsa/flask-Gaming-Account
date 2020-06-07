from flask import Flask, render_template, request, redirect, url_for, jsonify
from bson import ObjectId
from pymongo import MongoClient    
import hashlib

app = Flask(__name__)

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
    data = [
        {
            "_id" : data['nickname'],
            "fname" : data['fname'],
            "lname" : data['lname'],
            "phNum" : data['phNum'],
            "email" : data['email'],
            "pass" : hashlib.sha256(data['fpass'].encode()),
            "city" : data['city'],
            "country" : data['country']
        }
    ]

    res = users.insert(data)
    print(res)
    return redirect(url_for('index'))

@app.route('/login/', methods = ['POST'])
def login():
    if request.form == 'POST':
        data = request.form
    else:
        return redirect(url_for('index'))
    validate = authLogin(data)
    return redirect(url_for('index'))

def authLogin(data):
    usernameInp = data['usernameInp']
    passInp = data['passInp']

    if data.count_documents({"_id" : usernameInp}, limit = 1):
        for i in users.find_one({"__id": usernameInp}):
            if i['pass'] == hashlib.sha256(passInp).encode():
                return redirect(url_for('home'))
    else:
        return redirect(url_for('index'))

@app.route('/home/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    client = MongoClient("mongodb://127.0.0.1:27017")
    db = client['GamingAccount']
    users = db['users']
    app.run(debug = True)