import db, sqlite3

def add_recipe(ingredients, amounts, description, recipename, user_id):

    items = ""
    if not ingredients:
        items = "Ei ainesosia"
    else:
        items_list = [
            f"{i}: {a}" 
            for i, a in zip(ingredients, amounts)
            if i.strip() and a.strip()
        ]
        items = ",".join(items_list)

    sql = """INSERT INTO Recipes (name, user_id, description, items) VALUES
    (?, ?, ?, ?)"""
    try:
        db.execute(sql, [recipename, user_id, description, items])
    except sqlite3.IntegrityError:
        return "Tämä nimi jo käytössä reseptillä"

def get_recipes():
    sql = "SELECT id, name, description, items FROM Recipes ORDER BY id DESC;"
    return db.query(sql)

def get_recipe(recipe_id):
    sql = """SELECT recipes.name,
            users.username,
            recipes.description,
            recipes.items
            FROM Recipes
            JOIN Users ON recipes.user_id = Users.id
            AND recipes.id = ?"""
    return db.query(sql, [recipe_id])[0]
    

