from database import db
import bcrypt

# Define your models (if you have any)
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @staticmethod
    def get_by_username(username):
        cursor = db.cursor()
        query = "SELECT uid, passwd FROM user_login WHERE uid=%s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return User(result[0], result[1])
        return None

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
