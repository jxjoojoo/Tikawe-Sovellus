import db, sqlite3

def add_recipe(ingredients, amounts, description, recipename, user_id, section, time, choices):

    sql = """INSERT INTO Recipes (name, user_id, description, time) VALUES
    (?, ?, ?, ?)"""
    try:
        db.execute(sql, [recipename, user_id, description, time])
    except sqlite3.IntegrityError:
        return "name already_in_use"
    
    recipe_id = db.last_insert_id()
    
    sql = "INSERT INTO Ingredients (recipe_id, name, amount) VALUES (?, ?, ?)"
    for name, amount in zip(ingredients, amounts):
        db.execute(sql, [recipe_id, name, amount])
    
    sql = "DELETE FROM Recipe_classes WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])

    sql = "INSERT INTO Recipe_classes (recipe_id, title, value) VALUES (?, ?, ?)"
    for category, value in choices.items():
        db.execute(sql, [recipe_id, category, value])
    
    return recipe_id

def get_all_recipes():
    sql= """SELECT Recipes.id, Recipes.name, Recipes.description,
            Recipes.user_id, Users.username,
            COUNT(Comments.id) comment_count,
            (SELECT Images.id FROM Images
            WHERE Images.recipe_id = Recipes.id
            ORDER BY Images.id ASC LIMIT 1) image_id
            FROM Recipes 
            JOIN Users ON Recipes.user_id = Users.id
            LEFT JOIN Comments ON Recipes.id = Comments.recipe_id
            GROUP BY Recipes.id
            ORDER BY Recipes.id DESC"""
    #image = first added picture for each recipe

    return db.query(sql)

def get_ingredients(recipe_id):
    sql ="SELECT name, amount FROM Ingredients WHERE recipe_id = ?"
    return db.query(sql, [recipe_id])

def get_recipe(recipe_id):
    sql = """SELECT recipes.name,
            recipes.id,
            recipes.description,
            recipes.time,
            users.username,
            users.id user_id
            FROM Recipes
            JOIN Users ON recipes.user_id = Users.id
            AND recipes.id = ?"""
    result = db.query(sql, [recipe_id])
    return result[0] if result else None
    
def update_recipe(recipe_id, recipename, ingredients, description, section, time, classes, choices):
    sql = """UPDATE Recipes SET name = ?,
            description = ?,
            time = ?
            WHERE id = ?"""
    try:
        db.execute(sql, [recipename, description, time, recipe_id])
    except sqlite3.IntegrityError:
        return "name_already_in_use"

    sql = "DELETE FROM Ingredients WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])
    sql = "INSERT INTO Ingredients (recipe_id, name, amount) VALUES (?, ?, ?)"
    for ing in ingredients:
        db.execute(sql, [recipe_id, ing["name"], ing["amount"]])

    sql = "DELETE FROM Recipe_classes WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])

    sql = "INSERT INTO Recipe_classes (recipe_id, title, value) VALUES (?, ?, ?)"
    for category, value in choices.items():
        db.execute(sql, [recipe_id, category, value])

def add_comment(comment, recipe_id, user_id):
    sql = """INSERT INTO Comments (recipe_id, user_id, comment_str)
            VALUES (?, ?, ?)"""
    db.execute(sql, [recipe_id, user_id, comment])

def get_comment_author_and_recipe(comment_id):
    sql = """SELECT user_id, recipe_id
            FROM Comments WHERE id = ?"""
    result = db.query(sql, [comment_id])
    if not result:
        return None
    return result[0]

def remove_comment(comment_id):
    sql = "DELETE FROM Comments WHERE Comments.id = ?"
    db.execute(sql, [comment_id])

def get_comments(recipe_id):
    sql = """SELECT Comments.comment_str, Users.id AS user_id,
            Users.username, Comments.id
            FROM Comments, Users WHERE Comments.recipe_id = ?
            AND Comments.user_id = Users.id
            ORDER BY Comments.id DESC"""
    return db.query(sql, [recipe_id])

def add_image(recipe_id, image):
    sql = "INSERT INTO Images (recipe_id, image) VALUES (?, ?)"
    db.execute(sql, [recipe_id, image])

def get_images(recipe_id):
    sql = "SELECT id FROM images WHERE recipe_id = ?"
    return db.query(sql, [recipe_id])

def get_image(image_id):
    sql = "SELECT image FROM Images WHERE id = ?"
    result = db.query(sql, [image_id])
    return result[0][0] if result else None

def remove_image(recipe_id, image_id):
    sql = "DELETE FROM Images WHERE recipe_id = ? AND id = ?"
    db.execute(sql, [recipe_id, image_id])

def remove_recipe(recipe_id):
    sql = "DELETE FROM Recipe_classes WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])

    sql = "DELETE FROM Images WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])

    sql = "DELETE FROM Comments WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])

    sql = "DELETE FROM Ingredients WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])

    sql = "DELETE FROM Recipes WHERE id = ?"
    db.execute(sql, [recipe_id])

def find_recipes(query):
    sql = """SELECT R.id, R.name, R.user_id,
            U.username, COUNT(C.id) comment_count,
            (SELECT Images.id FROM Images
            WHERE Images.recipe_id = R.id
            ORDER BY Images.id ASC LIMIT 1) image_id
            FROM Recipes R
            JOIN Users U ON R.user_id = U.id
            LEFT JOIN Comments C ON R.id = C.recipe_id
            WHERE R.name LIKE ? OR R.description LIKE ?
            OR U.username LIKE ?
            GROUP BY R.id
            ORDER BY R.id DESC"""

    return db.query(sql, ["%" + query + "%", "%" + query + "%", "%" + query + "%"])

def get_classes(recipe_id):
    sql = "SELECT title, value FROM Recipe_classes WHERE recipe_id = ?"
    return db.query(sql, [recipe_id])

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = list(db.query(sql))
    classes = {}

    for title, value in result:
        if title not in classes:
            classes[title] = []
        classes[title].append(value)

    return classes