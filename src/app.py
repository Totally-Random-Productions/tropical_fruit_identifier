import shutil
from subprocess import PIPE, Popen

from flask import Flask, request, render_template, redirect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import uuid

app = Flask(__name__)
app.config["MONGO_URI"] = 'mongodb://localhost:27017/fruit_identifier'
CORS(app)
TEMPLATES_AUTO_RELOAD = True
mongo = PyMongo(app)

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


@app.route("/upload")
def uploadPage():
    return render_template("upload.html")


@app.route("/detected", methods=['POST', 'GET'])  # Used to save images to the database after being classified
def save_image():
    # need to change where the image is stored.  temporary
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
                print("Insert successful. 200")
            return uploadPage()
    except Exception as e:
        print("In save image")
        return render_template("error.html")



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}


@app.route("/upload", methods=['POST', 'GET'])
def upload_image():
    if request.method == 'POST':
        if get_image(request):
            print("image got")
            if detect():
                print("detected")
                return detectedPage()  # Verify object recogition, submit to database
            else:
                print("else")
                return uploadPage()    # Upload and try again
    return render_template("error.html")   # Something went wrong


def get_image(req):
    if 'upload_image' not in req.files:
        print('No file part')
        return False
    file = req.files['upload_image']
    if file.filename == '':
        print('No selected file')
        return False
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        manage_folders()
        file.save(os.path.join(detect_path, filename))
        return True
    return False


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


@app.route("/test1")
def detect():
    rc = Popen("python custom_detect.py").wait()
    print("something")
    if rc == 0:
        print("rc = ", rc)
        return True
    print("rc2 =", rc)
    return False


@app.route("/detected")
def detectedPage():
    label = getlabel()
    return render_template("detected.html", lb=label)


def getlabel():
    with open('data/temp/output_labels.txt') as labels:
        first = labels.readline()
        label = first.split('Label:')[-1].split(",")[0]
    return label


@app.route("/verify")
def get_images():
    pictures = []
    try:
        table = mongo.db.unverified_fruits
        for doc in table.find({}):
            pictures += ([doc])
    except Exception as e:
        print("No database :(")
    if not pictures:
        return render_template("empty.html")
    return render_template("verify.html", images=pictures)


@app.route("/verify")
def verify():
    return render_template("verify.html")


@app.route("/verify/remove/<file_id>", methods=['GET', 'DELETE'])
def remove_file(file_id):
    table = mongo.db.unverified_fruits
    result = delete_file(table, file_id)
    print(result)
    if result["error"] != 200:
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
        # os.remove(file)
        src_table.delete_one({'_id': ObjectId(file_id)})
        return ({"message": "Sucessfully moved", "error": 200})
    except Exception as e:
         return ({"message": "An error occured", "error": 500})




