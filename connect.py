import pymongo
from pymongo import MongoClient
import bcrypt

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['plant_disease_detection']
collection = db['users']

def hash_password(password):
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password

def store_user(username, password):
    # Check if username already exists
    if collection.find_one({"username": username}):
        print("Username already exists.")
        return

    # Hash the password
    hashed_password = hash_password(password)

    # Insert the user into the database
    user = {
        "username": username,
        "password": hashed_password
    }
    collection.insert_one(user)
    print("User created successfully.")

# Example usage:
username = "example_user"
password = "example_password"

# Store the user
store_user(username, password)