
import db, sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
def get_user(user_id):
    sql = """SELECT id, username
            FROM Users
            WHERE id = ? """
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_recipes(user_id):
    sql = """SELECT id, name
            FROM Recipes
            WHERE user_id = ?
            ORDER BY id DESC"""
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

        
    