import os
from flask import Flask, redirect, render_template, request, session
from PIL import Image
import torchvision.transforms.functional as TF
import CNN
import numpy as np
import torch
import pandas as pd
import sqlite3
import hashlib

import pymongo
from pymongo import MongoClient
import hashlib

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['plant_disease_detection']
collection = db['users']

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to check if the username and password are valid
def check_login(username, password):
    # Find the user with the given username
    user = collection.find_one({"username": username})
    if user:
        # If the user is found, check if the password matches
        password_hash = hash_password(password)
        if user["password"] == password_hash:  # user["password"] is the password hash stored in the database
            return True
    return False


disease_info = pd.read_csv('disease_info.csv' , encoding='cp1252')


model = CNN.CNN(4)    
model.load_state_dict(torch.load("plant_disease_model_1.pt"))
model.eval()

def prediction(image_path):
    image = Image.open(image_path)
    image = image.resize((224, 224))
    input_data = TF.to_tensor(image)
    input_data = input_data.view((-1, 3, 224, 224))
    output = model(input_data)
    output = output.detach().numpy()
    index = np.argmax(output)
    return index


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username already exists
        if collection.find_one({"username": username}):
            return render_template('register.html', error='Username already exists')

        # Hash the password before storing it
        hashed_password = hash_password(password)

        # Insert the new user into the MongoDB collection
        collection.insert_one({"username": username, "password": hashed_password})

        return redirect('/login')  # Redirect to login page after successful registration

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
               
        if check_login(username, password):
            return redirect('/home')  # Redirect to dashboard page upon successful login
        else:
            return render_template('login.html', error='Invalid username or password')  # Display error message on login page if authentication fails
           
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear the user session
    

    # Redirect the user to the login page
    return redirect('/login')

@app.route('/home')

def home_page():
    return render_template('home.html')

@app.route('/contact')
def contact():
    return render_template('contact-us.html')

@app.route('/index')
def ai_engine_page():
    return render_template('index.html')

@app.route('/mobile-device')
def mobile_device_detected_page():
    return render_template('mobile-device.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        image = request.files['image']
        filename = image.filename
        file_path = os.path.join('static/uploads', filename)
        image.save(file_path)
        print(file_path)
        pred = prediction(file_path)
        title = disease_info['disease_name'][pred]
        description =disease_info['description'][pred]
        prevent = disease_info['Possible Steps'][pred]
        image_url = disease_info['image_url'][pred]
        
        return render_template('submit.html' , title = title , desc = description , prevent = prevent , 
                               image_url = image_url , pred = pred )



if __name__ == '__main__':
    app.run(debug=True)
