from flask import Flask, render_template, request, redirect, url_for, make_response
from werkzeug.utils import secure_filename
import os
from models import User
from database import db
import time

# Create the Flask app
app = Flask(__name__)

# Configure the upload folder for storing images
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    username = request.cookies.get('user_auth')
    if not username or not User.get_by_username(username):
        return redirect(url_for('login'))  # Redirect to login if not authorized()

    # Fetch all the patient profiles from the database
    def fetch_dashboard_data_from_database():
        cursor = db.cursor()
        query = "SELECT `id`, `first_name`, `last_name`, `patient_image_path` FROM patient_profiles"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
    dashboard_data = fetch_dashboard_data_from_database()
    return render_template('dashboard.html', result=dashboard_data)


@app.route('/logout')
def logout():
    # Remove the user_auth cookie to log out the user
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('user_auth')
    return response

@app.route('/create')
def create():
    # Check if the user_auth cookie is present and valid
    username = request.cookies.get('user_auth')
    if not username or not User.get_by_username(username):
        return redirect(url_for('login'))  # Redirect to login if not authorized()

    return render_template('create.html')

@app.route('/create_submit', methods=['POST'])
def create_submit():
    # Check if the user_auth cookie is present and valid
    username = request.cookies.get('user_auth')
    if not username or not User.get_by_username(username):
        return redirect(url_for('login'))  # Redirect to login if not authorized()

    # Get the form data
    fname = request.form['first_name']
    lname = request.form['last_name']
    age = request.form['age']
    street = request.form['street_address']
    city = request.form['city']
    province = request.form['province']
    contact = request.form['contact']
    country = request.form['country']
    department = request.form['department']
    mri_scan = request.files['mri_scan']
    patient_image = request.files['patient_image']
    
    # Check if files are uploaded and save them to the server
    if mri_scan and patient_image:
        # Ensure the upload folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
   
   # Save the uploaded files with secure filenames
    mri_scan_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(mri_scan.filename))
    patient_image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(patient_image.filename))
    mri_scan.save(mri_scan_path)
    patient_image.save(patient_image_path)

    # Insert the data into the database
    cursor = db.cursor()
    query = "INSERT INTO patient_profiles (first_name, last_name, age, street_address, city, province, contact, country, department, mri_scan_path, patient_image_path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
    values = (fname, lname, age, street, city, province, contact, country, department, "uploads/" + mri_scan.filename, "uploads/" + patient_image.filename)
    cursor.execute(query, values)
    db.commit()
    cursor.close()
    time.sleep(5)
    return redirect(url_for('dashboard'))

# Edit endpoint
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_profile(id):
    # Check if the user is authenticated
    username = request.cookies.get('user_auth')
    if not username or not User.get_by_username(username):
        return redirect(url_for('login'))  # Redirect to login if not authorized

    # Fetch the profile data from the database based on the provided ID
    cursor = db.cursor()
    query = "SELECT * FROM patient_profiles WHERE id = %s"
    cursor.execute(query, (id,))
    profile_data = cursor.fetchone()
    cursor.close()

    if profile_data is None:
        # Profile with the provided ID does not exist
        return 'Profile not found', 404

    if request.method == 'POST':
        # Process the form submission for updating the profile
        # Retrieve form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        age = request.form['age']
        street_address = request.form['street_address']
        city = request.form['city']
        province = request.form['province']
        contact = request.form['contact']
        country = request.form['country']
        department = request.form['department']
        
        # Update the profile data in the database
        cursor = db.cursor()
        update_query = "UPDATE patient_profiles SET first_name = %s, last_name = %s, age = %s, street_address = %s, city = %s, province = %s, contact = %s, country = %s, department = %s WHERE id = %s"
        cursor.execute(update_query, (first_name, last_name, age, street_address, city, province, contact, country, department, id))
        db.commit()
        cursor.close()
        time.sleep(3)
        # Redirect to the profile view page after editing
        return redirect(url_for('profile', id=id))

    # Render the profile edit form with pre-filled data
    return render_template('edit_profile.html', profile=profile_data)


# Profile endpoint
@app.route('/profile/<id>')
def profile(id):
    cursor=db.cursor()
    patient_query = f"SELECT * FROM patient_profiles WHERE `id`={id}"
    cursor.execute(patient_query)
    patient_info = cursor.fetchall()
    cursor.close()
    return render_template('profile.html',patients=patient_info)

@app.route('/delete/<id>',methods=["GET"])
def delete_profile(id):
    cursor = db.cursor()
    delete_query = f"DELETE FROM `patient_profiles` WHERE `patient_profiles`.`id` = {id}"
    cursor.execute(delete_query)
    db.commit()
    cursor.close()

    return redirect(url_for('dashboard'))
