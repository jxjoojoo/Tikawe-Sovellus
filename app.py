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
    all_recipes = recipes.get_recipes()

    return render_template("index.html", all_recipes=all_recipes)

@app.route("/recipe/<int:recipe_id>")
def show_recipe(recipe_id):
    recipe = recipes.get_recipe(recipe_id)
    items = recipe[3]
    itemslist = items.split(",")
    print(itemslist)
    return render_template("show_recipe.html", recipe=recipe, itemslist=itemslist)
    

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

@app.route("/newrecipe", methods=["GET", "POST"])
@app.route("/newrecipe", methods=["GET", "POST"])
def newrecipe():
    count = int(request.form.get("count", 1))

    ingredients = []
    amounts = []

    for i in range(count):
        ingredients.append(request.form.get(f"ingredients{i}", ""))
        amounts.append(request.form.get(f"amounts{i}", ""))

    # 🔹 uudet
    recipename = request.form.get("recipename", "")
    description = request.form.get("description", "")

    if "add" in request.form:
        count += 1
        ingredients.append("")
        amounts.append("")

    return render_template(
        "newrecipe.html",
        count=count,
        ingredients=ingredients,
        amounts=amounts,
        recipename=recipename,
        description=description
    )

@app.route("/submit", methods=["POST"])
def submit():
    if "user_id" not in session:
        return "Et ole kirjautunut"

    count = int(request.form.get("count", 1))

    ingredients = []
    amounts = []

    for i in range(count):
        ing = request.form.get(f"ingredients{i}", "")
        amt = request.form.get(f"amounts{i}", "")

        if ing.strip() and amt.strip():
            ingredients.append(ing)
            amounts.append(amt)

    description = request.form.get("description", "")
    recipename = request.form.get("recipename", "")
    user_id = session["user_id"]

    if recipename == "" or description == "":
        return "Resepti vaatii lisää tietoja"
    else:
        recipes.add_recipe(ingredients, amounts, description, recipename, user_id)

    return render_template("submit.html")



