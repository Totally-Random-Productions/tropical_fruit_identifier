from flask import Flask, request, jsonify, render_template, make_response
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid
import json

app = Flask(__name__)
app.config["MONGO_URI"]='mongodb://localhost:27017/fruit_identifier'
TEMPLATES_AUTO_RELOAD = True
mongo=PyMongo(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/test")
def hello():
    return "Hello World!"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/upload")
def uploadPage():
    return render_template("upload.html")

@app.route("/upload", methods=['POST', 'GET'])
def upload_image():
    #need to change where the image is stored.  temporary
    if request.method=="POST":
        target = os.path.join(APP_ROOT, 'static/unverified-fruit')  
        if not os.path.isdir(target):
            os.mkdir(target) 
        table = mongo.db.unverified_fruits
        if 'upload_image' in request.files:
            upload = request.files["upload_image"]
            filename = secure_filename(str(uuid.uuid4()))
            destination = "/".join([target, filename])
            upload.save(destination)
            table.insert({'fruit_image': "/".join(["../static/unverified-fruit", filename])})
            print("Insert sucessfull.")
    return uploadPage()

@app.route("/verify")
def get_images():
    target = os.path.join(APP_ROOT, 'unverified-fruit')  
    table = mongo.db.unverified_fruits
    pictures=[]
    for doc in table.find({}):
        pictures += ([doc])
    print(pictures)
    return render_template("verify.html", images=pictures)



