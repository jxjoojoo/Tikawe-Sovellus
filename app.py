import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config
import recipes

app = Flask(__name__)
app.secret_key = config.secret_key


@app.route("/", methods=["GET","POST"])
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
    
        sql = "SELECT id, password_hash FROM Users WHERE username = ?"
        result = db.query(sql, [username])
        if len(result) == 0:
            return "Väärä runnus tai salasana"
        else:
            user_id = result[0][0]
            password_hash = result[0][1]
        
        if check_password_hash(password_hash, password):
            session["username"] = username
            session["user_id"] = user_id
            return redirect("/")
        else:
            return "Väärä runnus tai salasana"

@app.route("/logout")
def logout():
    del session["username"]
    del session["user_id"]
    return redirect("/")


@app.route("/register", methods=["POST", "GET"])
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    if len(username) == 0 or len(password1) == 0:
        return render_template("register.html")

    try:
        sql = "INSERT INTO Users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"

@app.route("/newrecipe", methods=["GET"])
def newrecipe():
    return render_template("newrecipe.html")

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        ingredients = request.form.getlist("ingredients[]")
        amounts = request.form.getlist("amounts[]")
        description = request.form["description"]
        recipename = request.form["recipename"]
        user_id = session["user_id"]

        recipes.add_recipe(ingredients, amounts, description, recipename, user_id)

    return render_template("submit.html")



