from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import os
import random
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from transformers import pipeline

app = Flask(__name__)
app.secret_key = "deepshield_secret_key"

# Create main uploads folder and subfolders
UPLOAD_FOLDER = "uploads"
IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, "images")
VIDEO_FOLDER = os.path.join(UPLOAD_FOLDER, "videos")
AUDIO_FOLDER = os.path.join(UPLOAD_FOLDER, "audio")
TEXT_FOLDER = os.path.join(UPLOAD_FOLDER, "text")
for folder in [UPLOAD_FOLDER, IMAGE_FOLDER, VIDEO_FOLDER, AUDIO_FOLDER, TEXT_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# AI Model (placeholder, you can extend for real detection)
image_model = pipeline("image-classification", model="google/vit-base-patch16-224")

# ---------------- DATABASE ---------------- #
def init_db():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    # Add gender and avatar columns
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        gender TEXT,
        avatar TEXT,
        password TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS uploads(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT,
        filetype TEXT,
        media_type TEXT,
        prediction TEXT,
        confidence REAL,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        gender = request.form["gender"]
        avatar = "male_ava.png" if gender=="Male" else "female_ava.png"
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO users (name,email,phone,gender,avatar,password)
        VALUES (?,?,?,?,?,?)
        """,(name,email,phone,gender,avatar,password))
        conn.commit()
        conn.close()
        return redirect("/login")
    return render_template("signup.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cur.fetchone()
        conn.close()
        if user and check_password_hash(user[6], password):
            session["user_id"]=user[0]
            session["name"]=user[1]
            session["avatar"]=user[5]
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid login")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("dashboard.html", name=session["name"], avatar=session["avatar"])

@app.route("/analyze")
def analyze():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("analyze.html")

@app.route("/detect", methods=["POST"])
def detect():
    if "user_id" not in session:
        return jsonify({"error": "login required"})

    media_type = request.form.get("type")

    # For text input
    if media_type == "text":
        text = request.form.get("text", "")
        if not text.strip():
            return jsonify({"error": "No text provided"})
        # Mock detection score
        score = random.randint(0, 100)
        label = "Fake" if score <= 40 else "Suspicious" if score <= 70 else "Real"
        filename = "text_submission.txt"

    else:
        # File input
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file uploaded"})

        filename = file.filename

        # Choose proper subfolder
        if media_type == "image":
            subfolder = "images"
        elif media_type == "video":
            subfolder = "videos"
        elif media_type == "audio":
            subfolder = "audio"
        else:
            return jsonify({"error": "Invalid media type"})

        folder_path = os.path.join(UPLOAD_FOLDER, subfolder)
        os.makedirs(folder_path, exist_ok=True)
        path = os.path.join(folder_path, filename)
        file.save(path)

        # Mock detection
        score = random.randint(0, 100)
        label = "Fake" if score <= 40 else "Suspicious" if score <= 70 else "Real"

    # Store in database
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO uploads (user_id, filename, filetype, prediction, confidence, timestamp)
        VALUES (?,?,?,?,?,?)
    """, (
        session["user_id"],
        filename,
        media_type,
        label,
        score,
        datetime.now()
    ))
    conn.commit()
    conn.close()

    return jsonify({
        "label": label,
        "confidence": score
    })
@app.route("/account")
def account():
    if "user_id" not in session:
        return redirect("/login")
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT filename,filetype,media_type,prediction,confidence,timestamp FROM uploads WHERE user_id=? ORDER BY timestamp DESC",(session["user_id"],))
    uploads = cur.fetchall()
    conn.close()
    return render_template("account.html",uploads=uploads,name=session["name"],avatar=session.get("avatar"))

@app.route("/media")
def media():
    return render_template("media.html")

@app.route("/why")
def why():
    return render_template("why.html")

if __name__=="__main__":
    app.run(debug=True)