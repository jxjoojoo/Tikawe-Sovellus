import sqlite3
from flask import Flask
from flask import abort, redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config
import recipes
import users

app = Flask(__name__)
app.secret_key = config.secret_key

def check_login():
    if "user_id" not in session:
        abort(403)

@app.route("/", methods=["GET","POST"])
def index():
    all_recipes = recipes.get_recipes()

    return render_template("index.html", all_recipes=all_recipes)

@app.route("/recipe/<int:recipe_id>")
def show_recipe(recipe_id):

    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)

    items = recipe["items"]
    itemslist = items.split(",")
    user_id = recipe["user_id"]

    sql = "SELECT username FROM Users WHERE id = ?"
    username = db.query(sql, [user_id])[0][0]
    classes = recipes.get_classes(recipe_id)
    
    section = classes[0] if classes else ""
    time = int(classes[1]) if classes else 0
    hours = time // 60
    minutes = time % 60

    return render_template("show_recipe.html", recipe=recipe, itemslist=itemslist,
                            username=username, section=section, hours=hours, minutes=minutes)
    

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
    
    user_id = users.check_login_id(username, password)
        
    if user_id:
        session["username"] = username
        session["user_id"] = user_id
        return redirect("/")
    else:
        return "Väärä runnus tai salasana"

@app.route("/logout")
def logout():
    if "user_id" in session:
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

    if len(username) == 0 or len(password1) == 0:
        return render_template("register.html")
    
    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return render_template("user_created.html", username=username)

@app.route("/newrecipe", methods=["GET", "POST"])
def newrecipe():

    check_login()

    count = int(request.form.get("count", 1))

    ingredients = []
    amounts = []

    for i in range(count):
        ingredients.append(request.form.get(f"ingredients{i}", ""))
        amounts.append(request.form.get(f"amounts{i}", ""))

    if "add" in request.form:
        count += 1
        ingredients.append("")
        amounts.append("")
    
    recipename = request.form.get("recipename", "")
    description = request.form.get("description", "")
    minutes = request.form.get("minutes")
    hours = request.form.get("hours")
    section = request.form.get("section")

    return render_template(
        "newrecipe.html",
        count=count,
        ingredients=ingredients,
        amounts=amounts,
        recipename=recipename,
        description=description,
        hours=hours,
        minutes=minutes,
        section=section
        
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
    
    hours = int(request.form.get("hours") or 0)
    minutes = int(request.form.get("minutes") or 0)
    time = hours * 60 + minutes
    section = request.form.get("section")
    recipename = request.form.get("recipename", "")
    description = request.form.get("description", "")

    if not recipename or len(recipename) > 50:
        abort(403)
    if not description or len(description) > 1000:
        abort(403)

    for i in ingredients:
        if len(i) > 50:
            abort(403)
    for j in amounts:
        if len(j) > 20:
            abort(403)

    user_id = session["user_id"]

    if recipename == "" or description == "":
        return "Resepti vaatii lisää tietoja"
    else:
        recipes.add_recipe(ingredients, amounts, description, recipename, user_id, section, time)

    return render_template("submit.html")

@app.route("/edit_recipe/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):

    recipe = recipes.get_recipe(recipe_id)

    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "POST":

        recipename = request.form.get("recipename")
        description = request.form.get("description")
        count = int(request.form.get("count", 1))

        ingredients = []

        for i in range(count):
            ing = request.form.get(f"ingredients{i}", "")
            if ing.strip():
                ingredients.append(ing)

        hours = int(request.form.get("hours") or 0)
        minutes = int(request.form.get("minutes") or 0)
        time = hours * 60 + minutes
        section = request.form.get("section")
        count = len(ingredients)

    
        if "add" in request.form:
            ingredients.append("")

        if "remove" in request.form:
            index = int(request.form.get("remove"))
            if 0 <= index < len(ingredients):
                ingredients.pop(index)

        if "save" in request.form:
            ingredients_str = ",".join(i for i in ingredients if i.strip())
            update_recipe(recipe_id, recipename, ingredients_str, description, section, time)
            return redirect("/recipe/" + str(recipe_id))
        
        count = len(ingredients)
        return render_template("edit.html", recipe=recipe, ingredients=ingredients, count=count, section=section, hours=hours, minutes=minutes)


    classes = recipes.get_classes(recipe_id)
    section = classes[0] if classes else ""
    time = classes[1] if classes else 0

    ingredients = recipe["items"].split(",") if recipe["items"] else [""]
    count = len(ingredients)

    hours = time // 60
    minutes = time % 60

    return render_template("edit.html", recipe=recipe, ingredients=ingredients, 
                                        count=count, section=section, hours=hours, minutes=minutes)

def update_recipe(recipe_id, recipename, ingredients, description, section, time):
    recipe = recipes.get_recipe(recipe_id)
    print("recipe user_id:", recipe["user_id"], type(recipe["user_id"]))
    print("session user_id:", session["user_id"], type(session["user_id"]))
    print("recipe_id:", recipe_id, type(recipe_id))
    print("recipename:", repr(recipename))
    print("description:", repr(description))
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)
    if not recipename or len(recipename) > 50:
        abort(403)
    if not description or len(description) > 1000:
        print("No description")
        abort(403)
    
    recipes.update_recipe(recipe_id, recipename, ingredients, description, section, time)

@app.route("/remove_recipe/<int:recipe_id>", methods=["GET", "POST"])
def remove_recipe(recipe_id):

    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        recipe = recipes.get_recipe(recipe_id)
        return render_template("remove_recipe.html", recipe=recipe)
    
    if request.method == "POST":

        if "remove" in request.form:
            recipes.remove_recipe(recipe_id)
            return redirect("/")

        if "dont" in request.form:
            return redirect("/recipe/" + str(recipe_id))

@app.route("/find_recipe")
def find_recipe():
    query = request.args.get("query")
    if query:
        results = recipes.find_recipes(query)
    else:
        query = ""
        results = []

    return render_template("find_recipe.html", query=query, results=results)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)

    recipes = users.get_recipes(user_id)
    return render_template("show_user.html", user=user, recipes=recipes)