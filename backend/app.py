from flask import Flask, render_template, request, redirect, url_for, make_response
import mysql.connector
import bcrypt
from werkzeug.utils import secure_filename
import os

# Create the Flask app
app = Flask(__name__)

# Configure the upload folder for storing images
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure your database connection
DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'project_gehen'

# Check cookies
def check_authentication():
    # Check if the user_auth cookie is present and valid
    username = request.cookies.get('user_auth')
    if not username or not User.get_by_username(username):
        return redirect(url_for('login'))  # Redirect to login if not authorized
    
# Connect to MySQL database
db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)


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


# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.get_by_username(username)

        if user and user.check_password(password):
            # Create a response with a cookie for user authorization
            response = make_response(redirect(url_for('dashboard')))
            response.set_cookie('user_auth', username, httponly=True)  # Set user_auth cookie

            return response

        # Invalid login credentials, show an error message
        error_message = "Invalid username or password. Please try again."
        return render_template('login.html', error_message=error_message)

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    # Check if the user_auth cookie is present and valid
    check_authentication()

    # Retrieve all patient profiles from the database
    db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    return render_template('dashboard.html')


@app.route('/logout')
def logout():
    # Remove the user_auth cookie to log out the user
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('user_auth')
    return response

if __name__ == '__main__':
    app.run(debug=True)