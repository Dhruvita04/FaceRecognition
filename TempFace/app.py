import face_recognition
import cv2
import numpy as np
import os
import csv
from datetime import datetime
import pickle
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

class AttendanceSystem:
    def __init__(self):
        self.users = {}
        self.admin_username = "admin"
        self.admin_password = "password123"
        self.load_users()

    def load_users(self):
        if os.path.exists('users.pkl'):
            with open('users.pkl', 'rb') as f:
                self.users = pickle.load(f)

    def save_users(self):
        with open('users.pkl', 'wb') as f:
            pickle.dump(self.users, f)

    def register_user(self, username):
        face_encoding = self.capture_face()
        if face_encoding is None:
            return "Failed to capture face. Please try again."

        if username in self.users:
            return f"User {username} already exists. Please choose a different name."

        self.users[username] = face_encoding
        self.save_users()
        return f"User {username} registered successfully!"

    def login_user(self):
        face_encoding = self.capture_face()
        if face_encoding is None:
            return "Failed to capture face. Please try again."

        for name, encoding in self.users.items():
            if face_recognition.compare_faces([encoding], face_encoding)[0]:
                session['user'] = name
                return f"Welcome, {name}!"

        return "Face not recognized. Please try again or register."

    def capture_face(self):
        video_capture = cv2.VideoCapture(0)
        if not video_capture.isOpened():
            return None

        while True:
            ret, frame = video_capture.read()
            if not ret:
                continue

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)

            if face_locations:
                face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
                video_capture.release()
                return face_encoding

        video_capture.release()
        return None

    def take_attendance(self, user_name):
        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d")
        time_string = now.strftime("%H:%M:%S")

        filename = f"attendance_{date_string}.csv"
        file_exists = os.path.isfile(filename)

        if file_exists:
            with open(filename, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['Name'] == user_name:
                        return f"Attendance already recorded for {user_name} today."

        with open(filename, 'a', newline='') as csvfile:
            fieldnames = ['Name', 'Date', 'Time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow({'Name': user_name, 'Date': date_string, 'Time': time_string})

        return f"Attendance recorded for {user_name}"

attendance_system = AttendanceSystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    if not username:
        return "Please provide a username", 400
    return attendance_system.register_user(username)

@app.route('/login')
def login():
    return attendance_system.login_user()

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    user_name = data.get('username')
    if not user_name:
        return "Please provide a username", 400
    return attendance_system.take_attendance(user_name)

@app.route('/admin_login', methods=['POST'])
def admin_login():
    data = request.json
    if data['username'] == attendance_system.admin_username and data['password'] == attendance_system.admin_password:
        session['admin'] = True
        return "Admin logged in successfully"
    return "Invalid admin credentials"

@app.route('/view_attendance', methods=['POST'])
def view_attendance():
    if 'admin' not in session:
        return "Unauthorized", 401
    
    data = request.json
    date = data.get('date')
    
    if not date:
        return "Please provide a date", 400
    
    filename = f"attendance_{date}.csv"
    
    if not os.path.exists(filename):
        return jsonify([])
    
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        attendance_data = list(reader)
    
    return jsonify(attendance_data)

@app.route('/update_attendance', methods=['POST'])
def update_attendance():
    if 'admin' not in session:
        return "Unauthorized", 401
    
    data = request.json
    date = data.get('date')
    name = data.get('name')
    new_time = data.get('new_time')
    
    if not all([date, name, new_time]):
        return "Missing required data", 400
    
    filename = f"attendance_{date}.csv"
    if not os.path.exists(filename):
        return "No attendance record for this date", 404
    
    temp_filename = f"temp_{filename}"
    updated = False
    
    with open(filename, 'r') as csvfile, open(temp_filename, 'w', newline='') as temp_csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(temp_csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            if row['Name'] == name:
                row['Time'] = new_time
                updated = True
            writer.writerow(row)
    
    os.replace(temp_filename, filename)
    
    if updated:
        return f"Attendance updated for {name} on {date}"
    else:
        return f"No attendance record found for {name} on {date}", 404

@app.route('/delete_attendance', methods=['POST'])
def delete_attendance():
    if 'admin' not in session:
        return "Unauthorized", 401
    
    data = request.json
    date = data.get('date')
    name = data.get('name')
    
    if not all([date, name]):
        return "Missing required data", 400
    
    filename = f"attendance_{date}.csv"
    if not os.path.exists(filename):
        return "No attendance record for this date", 404
    
    temp_filename = f"temp_{filename}"
    deleted = False
    
    with open(filename, 'r') as csvfile, open(temp_filename, 'w', newline='') as temp_csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(temp_csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            if row['Name'] != name:
                writer.writerow(row)
            else:
                deleted = True
    
    os.replace(temp_filename, filename)
    
    if deleted:
        return f"Attendance record deleted for {name} on {date}"
    else:
        return f"No attendance record found for {name} on {date}", 404

@app.route('/logout')
def logout():
    session.clear()
    return "Logged out successfully"

if __name__ == '__main__':
    app.run(debug=True)