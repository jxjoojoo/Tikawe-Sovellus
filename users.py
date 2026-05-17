import db
from werkzeug.security import check_password_hash, generate_password_hash
def get_user(user_id):
    sql = """SELECT id, username
            FROM Users
            WHERE id = ? """
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_recipes(user_id):
    sql = """SELECT Recipes.id, Recipes.name, COUNT(Comments.id) comment_count
            FROM Recipes LEFT JOIN Comments ON Recipes.id = Comments.recipe_id
            WHERE Recipes.user_id = ? GROUP BY Recipes.id
            ORDER BY Recipes.id DESC"""
    return db.query(sql, [user_id])

def create_user(name, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO Users (username, password_hash) VALUES (?,?)"
    db.execute(sql, [name, password_hash])

def check_login_id(name, password):
    sql = "SELECT id, password_hash FROM Users WHERE username = ?"
    result = db.query(sql, [name])

    if not result:
        return None
    else:
        user_id = result[0]["id"]
        password_hash = result[0]["password_hash"]

    if check_password_hash(password_hash, password):
        return user_id
    else:
        return None

def get_leaderboard():
    sql = """SELECT Users.username, Users.id, COUNT(Recipes.id) recipe_count FROM Users
            LEFT JOIN Recipes ON Recipes.user_id = Users.id
            GROUP BY Users.id
            ORDER BY recipe_count DESC
            LIMIT 5"""
    return db.query(sql)