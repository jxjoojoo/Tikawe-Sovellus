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
            recipes.id,
            recipes.description,
            recipes.items,
            users.username,
            users.id user_id
            FROM Recipes
            JOIN Users ON recipes.user_id = Users.id
            AND recipes.id = ?"""
    result = db.query(sql, [recipe_id])
    return result[0] if result else None
    
def update_recipe(recipe_id, recipe_name, items, description):
    sql = """UPDATE Recipes SET name = ?,
            description = ?,
            items = ?
            WHERE id = ?"""

    db.execute(sql, [recipe_name, description, items, recipe_id])

def remove_recipe(recipe_id):
    sql = "DELETE FROM Recipes WHERE id = ?"
    db.execute(sql, [recipe_id])

def find_recipes(query):
    sql = """SELECT id, name, user_id, items, description
            FROM Recipes WHERE name LIKE ? OR description LIKE ?
            OR items LIKE ?
            ORDER BY id DESC"""

    return db.query(sql, ["%" + query + "%", "%" + query + "%", "%" + query + "%"])
