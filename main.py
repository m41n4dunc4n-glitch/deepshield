from flask import Flask, render_template, request, redirect, session, send_from_directory, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random
import smtplib
from datetime import datetime  # ✅ ADDED
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "super_secret_key"

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "users.db")
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- EMAIL FUNCTION ----------------

def send_verification_email(receiver_email, code):

    sender_email = "ai.deepshield@gmail.com"
    sender_password = "fluvltqjvwhiyxip"

    subject = "DeepShield Verification Code"
    body = f"Your DeepShield verification code is: {code}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "DeepShield <ai.deepshield@gmail.com>"
    msg["To"] = receiver_email

    message = f"Subject: {subject}\n\n{body}"

    server = smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, message)
    server.quit()

# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        gender TEXT,
        avatar TEXT,
        password TEXT
    )
    """)

    # ✅ FIXED TABLE (ONLY ADDITIONS)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS uploads(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        file_type TEXT,
        filename TEXT,
        result TEXT,
        confidence INTEGER,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("home.html")

# ---------------- SIGNUP ----------------

@app.route("/signup", methods=["GET","POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        gender = request.form["gender"]
        password = request.form["password"]

        code = str(random.randint(100000,999999))

        session["verify_code"] = code
        session["signup_data"] = {
            "name": name,
            "email": email,
            "phone": phone,
            "gender": gender,
            "password": password
        }

        send_verification_email(email, code)

        return redirect("/verify")

    return render_template("signup.html")

# ---------------- VERIFY ----------------

@app.route("/verify", methods=["GET","POST"])
def verify():

    if request.method == "POST":

        if request.form["code"] == session.get("verify_code"):

            data = session.get("signup_data")

            avatar = "male_ava.png" if data["gender"] == "Male" else "female_ava.png"

            password = generate_password_hash(data["password"])

            conn = get_db()
            cur = conn.cursor()

            cur.execute("""
            INSERT INTO users (name,email,phone,gender,avatar,password)
            VALUES (?,?,?,?,?,?)
            """,(data["name"],data["email"],data["phone"],data["gender"],avatar,password))

            conn.commit()
            conn.close()

            return redirect("/login")

    return render_template("verify.html")

# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cur.fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["avatar"] = user["avatar"]
            session["gender"] = user["gender"]

            return redirect("/dashboard")

        return "Invalid login"

    return render_template("login.html")

# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM uploads")
    scans = cur.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        name=session["name"],
        avatar=session["avatar"],
        scans=scans
    )

# ---------------- ACCOUNT ----------------

@app.route("/account")
def account():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
SELECT * FROM uploads 
WHERE user_id=? 
ORDER BY id DESC
""", (session["user_id"],))    
    
    uploads = cur.fetchall()

    conn.close()

    # ✅ counts
    fake_count = 0
    real_count = 0
    suspicious_count = 0

    for u in uploads:
        result = u["result"].lower()

        if result == "fake":
            fake_count += 1
        elif result == "real":
            real_count += 1
        elif result == "suspicious":
            suspicious_count += 1

    return render_template(
        "account.html",
        uploads=uploads,
        name=session["name"],
        avatar=session["avatar"],
        gender=session["gender"],
        fake_count=fake_count,
        real_count=real_count,
        suspicious_count=suspicious_count
    )
# ---------------- ANALYZE ----------------

@app.route("/analyze")
def analyze():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("analyze.html")

# ---------------- DETECT ----------------

@app.route("/detect", methods=["POST"])
def detect():

    # -------- TEXT MODE --------
    text = request.form.get("text")

    if text and text.strip() != "":

        mode = random.choice(["Fake", "Suspicious", "Real"])

        if mode == "Fake":
            confidence = random.randint(0, 35)
            label = "Fake"

        elif mode == "Suspicious":
            confidence = random.randint(36, 56)
            label = "Suspicious"

        else:
            confidence = random.randint(57, 100)
            label = "Real"

        conn = get_db()
        cur = conn.cursor()

        date = datetime.now().strftime("%Y-%m-%d %H:%M")

        cur.execute("""
        INSERT INTO uploads (user_id, file_type, filename, result, confidence, date)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            "text",
            text[:20] + "...",
            label,
            confidence,
            date
        ))

        conn.commit()
        conn.close()

        return jsonify({"label": label, "confidence": confidence})


    # -------- FILE MODE --------
    if "file" not in request.files:
        return jsonify({"label": "No file", "confidence": 0})

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"label": "No file selected", "confidence": 0})


    mode = random.choice(["Fake", "Suspicious", "Real"])

    if mode == "Fake":
        confidence = random.randint(0, 35)
        label = "Fake"

    elif mode == "Suspicious":
        confidence = random.randint(36, 56)
        label = "Suspicious"

    else:
        confidence = random.randint(57, 100)
        label = "Real"


    file_type = request.form.get("type") or "image"

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    conn = get_db()
    cur = conn.cursor()

    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    cur.execute("""
    INSERT INTO uploads (user_id, file_type, filename, result, confidence, date)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        session["user_id"],
        file_type,
        file.filename,
        label,
        confidence,
        date
    ))

    conn.commit()
    conn.close()

    return jsonify({"label": label, "confidence": confidence})

# ---------------- DELETE ----------------

@app.route("/delete_upload", methods=["POST"])
def delete_upload():

    if "user_id" not in session:
        return jsonify({"status":"error"})

    data = request.get_json()
    upload_id = data.get("id")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
    "DELETE FROM uploads WHERE id=? AND user_id=?",
    (upload_id, session["user_id"])
)

    conn.commit()
    conn.close()

    return jsonify({"status":"deleted"})

    
#-----------------logout-------------- 
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- RUN ----------------

import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))