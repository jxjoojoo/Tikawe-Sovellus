import db, sqlite3

def add_recipe(ingredients, amounts, description, recipename, user_id):
    sql = """INSERT INTO Recipes (name, user_id, description) VALUES
    (?, ?, ?)"""
    try:
        db.execute(sql, [recipename, user_id, description])
    except sqlite3.IntegrityError:
        return "Tämä nimi jo käytössä reseptillä"
    
    recipe_id = db.last_insert_id()

    text = ""
    if len(ingredients) == 0:
        text += "Ei ainesosia"
    else:
        for ingredient, amount in zip(ingredients, amounts):
            text += f"{ingredient}: {amount},"
            
    text = text[:-1]

    sql = """INSERT INTO Ingredients (recipe_id, items) VALUES (?, ?)"""
    db.execute(sql, [recipe_id, text])