import shutil
from subprocess import PIPE, Popen

from flask import Flask, request, render_template, redirect, make_response, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from flask_cors import CORS 
from datetime import datetime
from flask_bcrypt import Bcrypt 
from flask_jwt_extended import  JWTManager, jwt_required, create_access_token, jwt_refresh_token_required, create_refresh_token, get_jwt_identity, set_access_cookies, unset_jwt_cookies
import os
import uuid

app = Flask(__name__)
app.config["MONGO_URI"]='mongodb://localhost:27017/fruit_identifier'
app.config['JWT_SECRET_KEY'] = 'secretysackity'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'

TEMPLATES_AUTO_RELOAD = True

mongo=PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)

#paths for saving files
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
unverified_path = "static/unverified-fruit"
detect_path = "data/temp"
veri_target = os.path.join(APP_ROOT, unverified_path)  

cocoa_path = "cocoa"
cocoa_target = os.path.join(APP_ROOT, cocoa_path) 

lemon_path = "lemon"
lemon_target = os.path.join(APP_ROOT, lemon_path) 

orange_path = "orange"
orange_target = os.path.join(APP_ROOT, orange_path) 

papaya_path = "papaya"
papaya_target = os.path.join(APP_ROOT, papaya_path) 


@app.route("/test")
def hello():
    return "Hello World!"


@app.route("/")
def home():
    return render_template("home.html")

#auth checks

@jwt.unauthorized_loader
def unauthorized_callback(callback):
    return redirect("/login", 302)

@jwt.invalid_token_loader
def invalid_token_callback(callback):
    resp = make_response(redirect("/login"))
    unset_jwt_cookies(resp)
    resp.set_cookie("access_token_cookie","")
    return resp, 302

@jwt.expired_token_loader
def expired_token_callback(callback):
    # Expired auth header
    resp = make_response(redirect("/login"))
    resp.set_cookie("access_token_cookie","")
    unset_jwt_cookies(resp)
    return resp, 302

#registration and login
@app.route('/logout')
def logout():
    unset_jwt_cookies(jsonify({'logout' : True}))
    resp= make_response(redirect("/"))
    resp.set_cookie("access_token_cookie","")
    return resp


@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route('/users/register', methods=['POST','GET'])
def register():
    try:
        users = mongo.db.users 
        first_name = request.get_json()['first_name']
        last_name = request.get_json()['last_name']
        email = request.get_json()['email']
        password = bcrypt.generate_password_hash(request.get_json()['password']).decode('utf-8')
        created = datetime.utcnow()

        user_id = users.insert({
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': password,
            'active':"NO", 
            'created': created 
        })

        new_user = users.find_one({'_id': user_id})

        result = {'email': new_user['email'] + ' registered'}
    
        return jsonify({'result' : result})
    except Exception as e:
        print(e)
        return jsonify({"Error":"An error occured"})


@app.route('/login', methods=['POST'])
def login():
    try:
        data=None
        if request.content_type  == 'application/x-www-form-urlencoded':
            data = request.form
        elif request.content_type == 'application/json':
            data = request.json
        email = data["email"]
        password = data['password']
        users = mongo.db.users 
        response = users.find_one({'email': email})
        if response:
            if bcrypt.check_password_hash(response['password'], password) and response['active']=="YES":
                access_token = create_access_token(identity = {
                    'first_name': response['first_name'],
                    'last_name': response['last_name'],
                    'email': response['email']
                })
                set_access_cookies(jsonify({'login': True}),access_token)
                resp= make_response(redirect("/verify"))
                resp.set_cookie("access_token_cookie",access_token)
                return resp
        return make_response(redirect("/login"))
    except Exception as e:
        print(e)
        return make_response(redirect("/login"))


#uploading images
@app.route("/upload")
def uploadPage():
    return render_template("upload.html")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@app.route("/upload", methods=['POST', 'GET'])
def upload_image():
    try:
        if request.method == 'POST':
            if 'upload_image' in request.files:
                upload = request.files["upload_image"]
                if get_image(upload):
                    if detect():
                        label = getlabel()
                        return render_template("detected.html", lb=label)# Verify object recogition, submit to database
                    else:
                        return uploadPage()    # Upload and try again
        return render_template("error.html")   # Something went wrong
    except Exception as e:
        print(e)
        return render_template("error.html")

def get_image(file):
    try:
        print(file)
        if file.filename == '':
            return False
        if file and allowed_file(file.filename):
            filename = secure_filename(str(uuid.uuid4())+file.filename)
            loc=os.path.join(detect_path, filename)
            manage_folders()
            file.save(loc)
            copy_unverified_image(loc,filename)
            return True
        return True
    except Exception as e:
        print(e)
        return False

def copy_unverified_image(source,filename):
    try:
        print("In save")
        if not os.path.isdir(veri_target):
            os.mkdir(veri_target) 
        table = mongo.db.unverified_fruits
        destination = "/".join([veri_target, filename])
        shutil.copyfile(source,destination)
        table.insert({'fruit_image': "/".join([unverified_path , filename])})
        print("Insert successful. 200")
    except Exception as e:
        print (e)
        return False
    return True


def manage_folders():
    if os.path.isdir("data/temp"):
        print("data/temp")
        shutil.rmtree("data/temp")
    os.makedirs("data/temp", exist_ok=True)
    if os.path.isdir("static/css/img/temp"):
        print("static")
        shutil.rmtree("static/css/img/temp")
    os.makedirs("static/css/img/temp", exist_ok=True)
    print("end of manage")
    return


def detect():
    rc = Popen("python custom_detect.py", shell=True).wait()
    if rc == 0:
        print("rc = ", rc)
        return True
    print("rc2 =", rc)
    return False

def getlabel():
    with open('data/temp/output_labels.txt') as labels:
        first = labels.readline()
        label = first.split('Label:')[-1].split(",")[0]
    return label

#verifying images

@app.route("/verify")
@jwt_required
def get_images():
    pictures = []
    try:
        table = mongo.db.unverified_fruits
        for doc in table.find({}):
            pictures += ([doc])
    except Exception as e:
        print("No database :(")
        return render_template("error.html")
    if not pictures:
        return render_template("empty.html")
    return render_template("verify.html", images=pictures)

@app.route("/verify/remove/<file_id>", methods=['GET', 'DELETE'])
@jwt_required
def remove_file(file_id):
    table = mongo.db.unverified_fruits
    result = delete_file(table, file_id)
    print(result)
    if result["error"] != 200:
        return render_template("error.html", error=result)
    return redirect('/verify')


@app.route("/verify/cocoa/<file_id>", methods=['GET'])
@jwt_required
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
@jwt_required
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
@jwt_required
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
@jwt_required
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
        # os.remove(file)
        src_table.delete_one({'_id': ObjectId(file_id)})
        return ({"message": "Sucessfully moved", "error": 200})
    except Exception as e:
         return ({"message": "An error occured", "error": 500})




