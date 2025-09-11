from flask import Flask, request, jsonify, render_template, send_from_directory, redirect
import os
import sqlite3
import face_recognition
import numpy as np
import pickle
import base64
from io import BytesIO
from PIL import Image
import csv

app = Flask(__name__)

# === Folders and Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTO_FOLDER = os.path.join(BASE_DIR, "pre_registered", "photos")
DB_PATH = os.path.join(BASE_DIR, "pre_registered", "database.db")
CSV_PATH = os.path.join(BASE_DIR, "pre_registered", "users.csv")

os.makedirs(PHOTO_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# === Initialize database ===
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    organization TEXT,
                    phone TEXT,
                    email TEXT,
                    photo_path TEXT,
                    face_encoding BLOB
                )''')
    conn.commit()
    conn.close()

init_db()

# === Routes ===

@app.route('/')
def home():
    return redirect('/preregister')

@app.route('/pre_registered/photos/<path:filename>')
def serve_photos(filename):
    return send_from_directory(PHOTO_FOLDER, filename)

@app.route('/preregister', methods=['GET', 'POST'])
def preregister():
    if request.method == 'GET':
        return render_template('pre_register.html')

    try:
        name = request.form['name']
        organization = request.form['organization']
        phone = request.form['phone']
        email = request.form['email']
        photo = request.files['photo']

        if not all([name, organization, phone, email, photo]):
            return jsonify({'success': False, 'message': 'All fields are required.'})

        filename = f"{name}_{phone}.png"
        filepath = os.path.join(PHOTO_FOLDER, filename)
        photo.save(filepath)

        img = face_recognition.load_image_file(filepath)
        encodings = face_recognition.face_encodings(img)
        if not encodings:
            os.remove(filepath)
            return jsonify({'success': False, 'message': 'No face detected in photo.'})
        face_encoding = encodings[0]

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO users (name, organization, phone, email, photo_path, face_encoding) VALUES (?, ?, ?, ?, ?, ?)',
                  (name, organization, phone, email, os.path.join("pre_registered","photos",filename), pickle.dumps(face_encoding)))
        conn.commit()
        conn.close()

        file_exists = os.path.isfile(CSV_PATH)
        with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Name', 'Organization', 'Phone', 'Email', 'Photo Path'])
            writer.writerow([name, organization, phone, email, os.path.join("pre_registered","photos",filename)])

        return jsonify({'success': True, 'message': f'{name} registered successfully!'})

    except Exception as e:
        print("Error in /preregister:", e)
        return jsonify({'success': False, 'message': 'Registration failed.'})

# === Scan face route (robust matching) ===
@app.route('/scan_face', methods=['POST'])
def scan_face():
    try:
        data = request.get_json()
        if 'image' not in data:
            return jsonify({'found': False})

        img_data = data['image'].split(',')[1]
        img_bytes = base64.b64decode(img_data)
        img = Image.open(BytesIO(img_bytes)).convert('RGB')
        img_array = np.array(img)

        encodings_in_frame = face_recognition.face_encodings(img_array)
        if not encodings_in_frame:
            return jsonify({'found': False})
        frame_encoding = encodings_in_frame[0]

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name, organization, phone, email, photo_path, face_encoding FROM users")
        users = c.fetchall()
        conn.close()

        best_match = None
        best_distance = 1.0  # Maximum distance

        for user in users:
            name, org, phone, email, photo_path, face_enc_blob = user
            try:
                face_enc = pickle.loads(face_enc_blob)
            except:
                continue

            distance = face_recognition.face_distance([face_enc], frame_encoding)[0]
            if distance < 0.6 and distance < best_distance:
                best_distance = distance
                best_match = {
                    'name': name,
                    'organization': org,
                    'phone': phone,
                    'email': email,
                    'photo_path': '/' + photo_path.replace("\\","/")
                }

        if best_match:
            return jsonify({'found': True, **best_match})
        return jsonify({'found': False})

    except Exception as e:
        print("Error in /scan_face:", e)
        return jsonify({'found': False})

# === Event page route ===
@app.route('/event')
def event_page():
    return render_template('event.html')

# === Latest attendee route ===
@app.route('/latest_attendee')
def latest_attendee():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name, organization, photo_path FROM users ORDER BY id DESC LIMIT 1")
        user = c.fetchone()
        conn.close()

        if user:
            name, org, photo = user
            return jsonify({
                'name': name,
                'organization': org,
                'photo_path': '/' + photo.replace("\\","/")
            })
        return jsonify({})
    except Exception as e:
        print("Error in /latest_attendee:", e)
        return jsonify({})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT if available, else 5000 locally
    debug_mode = True if os.environ.get("PORT") is None else False  # Debug locally only
    app.run(host="0.0.0.0", port=port, debug=debug_mode)