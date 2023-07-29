import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
# Configure your database connection
DB_HOST = os.getenv("hostname")
DB_USER = os.getenv("username")
DB_PASSWORD = os.getenv("password")
DB_NAME = os.getenv("dbname")

    
# Connect to MySQL database
db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)