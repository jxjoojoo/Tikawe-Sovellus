import sqlite3
from flask import Flask
from flask import abort, redirect, render_template, flash, request, session, make_response
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
    all_recipes = recipes.get_all_recipes()
    recipes_count = len(all_recipes)
    return render_template("index.html", all_recipes=all_recipes, recipes_count=recipes_count)

@app.route("/recipe/<int:recipe_id>")
def show_recipe(recipe_id):

    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)

    ingredients = recipes.get_ingredients(recipe_id)
    user_id = recipe["user_id"]

    sql = "SELECT username FROM Users WHERE id = ?"
    username = db.query(sql, [user_id])[0][0]
    classes = recipes.get_classes(recipe_id)

    comments = recipes.get_comments(recipe_id)
    images = recipes.get_images(recipe_id)

    time = int(recipe["time"]) if recipe["time"] else 0
    hours = time // 60
    minutes = time % 60

    return render_template("show_recipe.html", recipe=recipe, ingredients=ingredients,
                            username=username, hours=hours,
                            minutes=minutes, classes=classes,
                            comments=comments, images=images)

@app.route("/image/<int:image_id>")
def show_image(image_id):
    image = recipes.get_image(image_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            flash("Kenttiä tyhjänä")
            return redirect("/login")
    
    user_id = users.check_login_id(username, password)
        
    if user_id:
        session["username"] = username
        session["user_id"] = user_id
        flash("Kirjautuminen onnistui")
        return redirect("/")
    else:
        flash("Väärä runnus tai salasana")
        return redirect("/login")

@app.route("/images/<int:recipe_id>")
def edit_images(recipe_id):
    check_login()
    recipe = recipes.get_recipe(recipe_id)

    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)

    images = recipes.get_images(recipe_id)
    
    return render_template("images.html", recipe=recipe, images=images)

@app.route("/add_image", methods=["POST"])
def add_image():
    check_login()
    recipe_id = request.form["recipe_id"]
    recipe = recipes.get_recipe(recipe_id)

    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("add_image.html")

    if request.method == "POST":
        file = request.files["image"]
        if not file.filename.endswith(".jpg"):
            return "VIRHE: väärä tiedostomuoto"

        image = file.read()
        if len(image) > 100 * 1024:
            return "VIRHE: liian suuri kuva"
        user_id = session["user_id"]
        recipes.add_image(recipe_id, image)
        return redirect("/images/" + str(recipe_id))
    
@app.route("/remove_image", methods=["POST"])
def remove_image():
    check_login()
    recipe_id = request.form["recipe_id"]
    recipe = recipes.get_recipe(recipe_id)

    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)

    for image_id in request.form.getlist("image_id"):
        recipes.remove_image(recipe_id, image_id)
    
    return redirect("/images/" + str(recipe_id))

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["username"]
        del session["user_id"]
    flash("Olet nyt kirjautunut ulos")
    return redirect("/message")

@app.route("/register", methods=["POST", "GET"])
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create_new_account():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if password1 != password2:
        flash("VIRHE: Salasanat eivät ole samat")
        return redirect("/register")

    if len(username) == 0 or len(password1) == 0:
        flash("VIRHE: Puuttuvia kenttiä")
        return redirect("/register")
    
    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("VIRHE: Tunnus on jo varattu")
        return redirect("/register")

    flash("Tunnus luotu!")
    return redirect("/message")

@app.route("/message")
def message():
    #redirect("/message?prev={edellinen sivu}") kun ohjaus muualle
    prev = request.args.get("prev", "/")
    return render_template("message.html", prev=prev)

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
    classes = recipes.get_all_classes()
    choices = {}

    for c in classes:
        choices[c] = "(valitse)"

    if "submitrecipe" in request.form:
        if not description:
            flash("Kirjoita reseptille ohje!")
            return render_template(
                "newrecipe.html",
                count=count,
                ingredients=ingredients,
                amounts=amounts,
                recipename=recipename,
                description=description,
                hours=hours,
                minutes=minutes,
                section=section,
                classes=classes,
                choices=choices)

    if request.method == "POST":
        choices = {}
        for category in classes:
            value = request.form.get(f"class_{category}", "")
            choices[category] = value if value else "(valitse)"

    return render_template(
        "newrecipe.html",
        count=count,
        ingredients=ingredients,
        amounts=amounts,
        recipename=recipename,
        description=description,
        hours=hours,
        minutes=minutes,
        section=section,
        classes=classes,
        choices=choices
        
    )

@app.route("/submit", methods=["GET","POST"])
def submit_new_recipe():
    check_login()

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
    if hours < 0:
        abort(403)
    minutes = int(request.form.get("minutes") or 0)
    if minutes < 0:
        abort(403)
    
    time = hours * 60 + minutes
    section = request.form.get("section")
    recipename = request.form.get("recipename", "")
    description = request.form.get("description", "")
    classes = recipes.get_all_classes()

    choices = {}
    for group in classes.keys():
        if request.form.get(f"class_{group}"):
            choices[group] = request.form.get(f"class_{group}")

    if not recipename or len(recipename) > 50:
        abort(403)
    if not description or len(description) > 1000:
        flash("Kirjoita reseptille ohje!")
        return render_template(
        "newrecipe.html",
        count=count,
        ingredients=ingredients,
        amounts=amounts,
        recipename=recipename,
        description=description,
        hours=hours,
        minutes=minutes,
        section=section,
        classes=classes,
        choices=choices)

    for i in ingredients:
        if len(i) > 50:
            abort(403)
    for j in amounts:
        if len(j) > 20:
            abort(403)

    user_id = session["user_id"]

    if recipename == "" or description == "":
        flash("Puuttuvia tietoja!")
        return redirect("/newrecipe")
    else:
        recipe_id = recipes.add_recipe(ingredients, amounts, description, recipename, user_id, section, time, choices)
        if recipe_id == "name already_in_use":
            flash("nimi on jo käytössä, valitse toinen nimi")
            return render_template(
            "newrecipe.html",
            count=count,
            ingredients=ingredients,
            amounts=amounts,
            recipename=recipename,
            description=description,
            hours=hours,
            minutes=minutes,
            section=section,
            classes=classes,
            choices=choices)
        flash("Resepti lisätty!")
        return redirect(F"/message?prev=/recipe/{recipe_id}")

@app.route("/submit_comment", methods=["POST"])
def newcomment():
    check_login()
    comment = request.form.get("comment", "")
    recipe_id = request.form.get("recipe_id", "")
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    user_id = session["user_id"]
    recipes.add_comment(comment, recipe_id, user_id)
    return redirect(f"/recipe/{recipe_id}")

@app.route("/edit_recipe/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    check_login()
    recipe = recipes.get_recipe(recipe_id)

    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)
    
    images = recipes.get_images(recipe_id)

    if request.method == "POST":
        recipename = request.form.get("recipename")
        description = request.form.get("description")
        count = int(request.form.get("count", 1))

        ingredients = []
        for i in range(count):
            ing = request.form.get(f"ingredients{i}", "")
            amt = request.form.get(f"amounts{i}", "")
            if ing.strip():
                ingredients.append({"name": ing, "amount": amt})

        hours = int(request.form.get("hours") or 0)
        minutes = int(request.form.get("minutes") or 0)
        if minutes < 0:
            return redirect(f"/edit_recipe/{recipe_id}")
        
        time = hours * 60 + minutes
        section = request.form.get("section")
        classes = recipes.get_all_classes()

        choices = {}
        for group in classes.keys():
            if request.form.get(f"class_{group}"):
                choices[group] = request.form.get(f"class_{group}")


        if "add" in request.form:
            ingredients.append({"name": "", "amount": ""})

        if "remove" in request.form:
            index = int(request.form.get("remove"))
            if 0 <= index < len(ingredients):
                ingredients.pop(index)

        if "save" in request.form:
            if not description:
                flash("Kirjoita reseptille ohje!")
                return render_template(
                "edit.html",
                recipe=recipe,
                count=count,
                ingredients=ingredients,
                recipename=recipename,
                description=description,
                hours=hours,
                minutes=minutes,
                section=section,
                classes=classes,
                choices=choices,
                images=images)
            recipes.update_recipe(recipe_id, recipename, ingredients, description, section, time, classes, choices)
            flash("Resepti päivitetty!")
            return redirect(f"/message?prev=/recipe/{recipe_id}")
        
        count = len(ingredients)
        return render_template("edit.html", recipe=recipe,
                                            ingredients=ingredients,
                                            description=description,
                                            count=count, section=section,
                                            hours=hours, minutes=minutes,
                                            classes=classes, choices=choices,
                                            images=images)



    ingredients_data = recipes.get_ingredients(recipe_id)
    ingredients = [{"name": row["name"], "amount": row["amount"]} for row in ingredients_data] or [{"name": "", "amount": ""}]
    description = recipe["description"]
    count = len(ingredients)

    classes = recipes.get_all_classes()
    classes_data = recipes.get_classes(recipe_id)
    #-> [<sqlite object>, <sqlite object>]
    section = classes_data[0] if classes_data else ""
    time = int(recipe["time"]) if recipe["time"] else 0

    hours = time // 60
    minutes = time % 60

    choices = {category: "(valitse)" for category in classes}

    for row in classes_data:
        title = row[0]
        value = row[1]
        choices[title] = value

    for category, options in classes.items():
        if section in options:
            choices[category] = section

    return render_template("edit.html", recipe=recipe, ingredients=ingredients, description=description,
                                        count=count, section=section, hours=hours,
                                        minutes=minutes, classes=classes, choices=choices, images=images)

def update_recipe(recipe_id, recipename, ingredients, description, section, time, classes, choices):
    recipe = recipes.get_recipe(recipe_id)
    print(recipe)

    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)
    if not recipename:
        abort(403)
    if len(recipename) > 50:
        abort(403)
    if not description:
        abort(403)
    if len(description) > 1000:
        abort(403)
    
    recipes.update_recipe(recipe_id, recipename, ingredients, description, section, time, classes, choices)

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
            flash("Resepti poistettu!")
            return redirect("/message")

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

@app.route("/leaderboard")
def leaderboard():
    leaderboard = users.get_leaderboard()
    return render_template("leaderboard.html", leaderboard=leaderboard)