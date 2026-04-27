import db, sqlite3
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
    