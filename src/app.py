from flask import Flask, request, jsonify, render_template, make_response, redirect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_cors import CORS
import os
import uuid
import json

app = Flask(__name__)
app.config["MONGO_URI"]='mongodb://localhost:27017/fruit_identifier'
CORS(app)
TEMPLATES_AUTO_RELOAD = True
mongo=PyMongo(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
unverified_path = "static/unverified-fruit"
veri_target = os.path.join(APP_ROOT, unverified_path)  

cocoa_path= "static/cocoa"
cocoa_target = os.path.join(APP_ROOT, cocoa_path) 

lemon_path= "static/lemon"
lemon_target = os.path.join(APP_ROOT, lemon_path) 

orange_path= "static/orange"
orange_target = os.path.join(APP_ROOT, orange_path) 

papaya_path= "static/papaya"
papaya_target = os.path.join(APP_ROOT, papaya_path) 

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
    try:
        if request.method=="POST":
            if not os.path.isdir(veri_target):
                os.mkdir(veri_target) 
            table = mongo.db.unverified_fruits
            if 'upload_image' in request.files:
                upload = request.files["upload_image"]
                filename = secure_filename(str(uuid.uuid4()))
                destination = "/".join([veri_target, filename])
                upload.save(destination)
                table.insert({'fruit_image': "/".join([unverified_path , filename])})
                print("Insert sucessfull. 200")
        return uploadPage()
    except Exception as e:
        return render_template("error.html")

    
@app.route("/verify")
def get_images():
    pictures=[]
    try:
        table = mongo.db.unverified_fruits
        for doc in table.find({}):
            pictures += ([doc])
    except Exception as e:
        print("No database :(")
    if pictures==[]:
        return render_template("empty.html")
    return render_template("verify.html", images=pictures)

@app.route("/verify/remove/<file_id>", methods=['GET', 'DELETE'])
def remove_file(file_id):
    table = mongo.db.unverified_fruits
    result = delete_file(table, file_id)
    print(result)
    if result["error"]!=200:
        return render_template("error.html", error=result)
    return redirect('/verify')

@app.route("/verify/cocoa/<file_id>", methods=['GET'])
def add_cocoa(file_id):
    if not os.path.isdir(cocoa_target):
            os.mkdir(cocoa_target) 
    table = mongo.db.unverified_fruits
    result = move_file(cocoa_target, table, file_id)
    print(result)
    if result["error"]!=200:
        return render_template("error.html")
    return redirect('/verify')

@app.route("/verify/lemon/<file_id>", methods=['GET'])
def add_lemon(file_id):
    if not os.path.isdir(lemon_target):
            os.mkdir(lemon_target) 
    table = mongo.db.unverified_fruits
    result = move_file(lemon_target, table, file_id)
    print(result)
    if result["error"]!=200:
        return render_template("error.html")
    return redirect('/verify')

@app.route("/verify/orange/<file_id>", methods=['GET'])
def add_orange(file_id):
    if not os.path.isdir(orange_target):
            os.mkdir(orange_target) 
    table = mongo.db.unverified_fruits
    result = move_file(orange_target, table, file_id)
    print(result)
    if result["error"]!=200:
        return render_template("error.html")
    return redirect('/verify')

@app.route("/verify/papaya/<file_id>", methods=['GET'])
def add_papaya(file_id):
    if not os.path.isdir(papaya_target):
            os.mkdir(papaya_target) 
    table = mongo.db.unverified_fruits
    result = move_file(papaya_target, table, file_id)
    print(result)
    if result["error"]!=200:
        return render_template("error.html")
    return redirect('/verify')

def delete_file(table, file_id):
    try:
        file=table.find_one({'_id': ObjectId(file_id)})["fruit_image"]
        table.delete_one({'_id': ObjectId(file_id)})
        os.remove(file)
        return ({"message": "Sucessfully deleted", "error": 200})
    except Exception as e:
         return ({"message": "An error occured", "error": 500})
    
def move_file(destination, src_table, file_id):
    try:
        file=src_table.find_one({'_id': ObjectId(file_id)})["fruit_image"]
        filename = secure_filename(str(uuid.uuid4()))
        destination = "/".join([destination, filename])
        os.rename(file, destination)
        os.remove(file)
        src_table.delete_one({'_id': ObjectId(file_id)})
        return ({"message": "Sucessfully moved", "error": 200})
    except Exception as e:
         return ({"message": "An error occured", "error": 500})




