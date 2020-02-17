from flask import Flask, request, jsonify, render_template, make_response

app = Flask(__name__)

@app.route("/test")
def hello():
    return "Hello World!"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/upload")
def uploadPage():
    return render_template("upload.html")

