from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    send_from_directory,
    jsonify,
)
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import os
import random
from datetime import datetime  # ✅ ADDED
from email.mime.text import MIMEText


app = Flask(__name__)
app.secret_key = "super_secret_key"

import os

import requests

HF_API_URL = "https://api-inference.huggingface.co/models/dima806/deepfake_vs_real_image_detection"
HF_HEADERS = {
    "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
    "Content-Type": "application/octet-stream",
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "users.db")
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- EMAIL FUNCTION ----------------


def send_verification_email(receiver_email, code):
    try:
        receiver_email = receiver_email.strip().lower()

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = os.environ.get("BREVO_API_KEY")

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": receiver_email}],
            sender={"name": "DeepShield", "email": "ai.deepshield@gmail.com"},
            subject="DeepShield Verification Code",
            html_content=f"<h2>Your DeepShield verification code is: {code}</h2>",
        )

        api_instance.send_transac_email(send_smtp_email)
        print("EMAIL SENT ✅")

    except Exception as e:
        print("EMAIL ERROR ❌:", e)
        print("⚠️ FALLBACK CODE:", code)


# ---------------- DATABASE ----------------


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        gender TEXT,
        avatar TEXT,
        password TEXT
    )
    """
    )

    # ✅ FIXED TABLE (ONLY ADDITIONS)
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS uploads(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        file_type TEXT,
        filename TEXT,
        result TEXT,
        confidence INTEGER,
        date TEXT
    )
    """
    )

    conn.commit()
    conn.close()


init_db()

# ---------------- ROUTES ----------------


@app.route("/")
def home():
    return render_template("home.html")


# ---------------- SIGNUP ----------------


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        gender = request.form["gender"]
        password = request.form["password"]

        code = str(random.randint(100000, 999999))

        session["verify_code"] = code
        session["signup_data"] = {
            "name": name,
            "email": email,
            "phone": phone,
            "gender": gender,
            "password": password,
        }

        send_verification_email(email, code)

        return redirect("/verify")

    return render_template("signup.html")


# ---------------- VERIFY ----------------


@app.route("/verify", methods=["GET", "POST"])
def verify():

    if request.method == "POST":

        if request.form["code"] == session.get("verify_code"):

            data = session.get("signup_data")

            avatar = "male_ava.png" if data["gender"] == "Male" else "female_ava.png"

            password = generate_password_hash(data["password"])

            conn = get_db()
            cur = conn.cursor()

            # Check if email already exists
            cur.execute("SELECT * FROM users WHERE email = ?", (data["email"],))
            existing_user = cur.fetchone()

            if existing_user:
                return "Email already registered. Please login instead.", 400
                return redirect("/login")

            # If not exists → insert
            cur.execute(
                """
            INSERT INTO users (name,email,phone,gender,avatar,password)
            VALUES (?,?,?,?,?,?)
            """,
                (
                    data["name"],
                    data["email"],
                    data["phone"],
                    data["gender"],
                    avatar,
                    password,
                ),
            )

            conn.commit()
            conn.close()

            return redirect("/login")

    return render_template("verify.html")


# ---------------- LOGIN ----------------


@app.route("/login", methods=["GET", "POST"])
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
        "dashboard.html", name=session["name"], avatar=session["avatar"], scans=scans
    )


# ---------------- ACCOUNT ----------------


@app.route("/account")
def account():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
SELECT * FROM uploads 
WHERE user_id=? 
ORDER BY id DESC
""",
        (session["user_id"],),
    )

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
        suspicious_count=suspicious_count,
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
        try:
            # 🔹 BASIC CLEANING
            lower_text = text.lower()

            # 🔹 RULE 1: gibberish / too short
            if len(lower_text) < 5 or lower_text.isdigit():
                label = "Suspicious"
                confidence = 50

            # 🔹 RULE 2: scam keyword scoring
            scam_keywords = [
                "win",
                "free",
                "money",
                "click",
                "offer",
                "urgent",
                "prize",
                "lottery",
                "rich",
                "scam",
                "earn",
                "cash",
                "bonus",
                "guarantee",
                "investment",
                "double",
                "profit",
                "limited",
                "act now",
                "quick",
                "instant",
            ]

            matches = sum(word in lower_text.split() for word in scam_keywords)

            if matches >= 2:
                label = "Fake"
                confidence = 85

            elif matches == 1:
                label = "Suspicious"
                confidence = 60

            # 🔹 RULE 3: very short messages
            elif len(lower_text.split()) <= 3:
                label = "Suspicious"
                confidence = 55

            # 🔹 OTHERWISE → SAFE DEFAULT
            else:
                label = "Real"
                confidence = 80

        except Exception as e:
            print("AI Error:", e)
            label = "Suspicious"
            confidence = 50

        conn = get_db()
        cur = conn.cursor()

        date = datetime.now().strftime("%Y-%m-%d %H:%M")

        cur.execute(
            """
            INSERT INTO uploads (user_id, file_type, filename, result, confidence, date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session["user_id"], "text", text[:20] + "...", label, confidence, date),
        )

        conn.commit()
        conn.close()

        return jsonify({"label": label, "confidence": confidence})

    # -------- FILE MODE --------
    if "file" not in request.files:
        return jsonify({"label": "No file", "confidence": 0})

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"label": "No file selected", "confidence": 0})

    filename = file.filename.lower()

    # 🔹 HANDLE VIDEO
    if filename.endswith((".mp4", ".avi", ".mov")):
        return jsonify({"label": "Coming Soon", "confidence": 0})

    # 🔹 HANDLE AUDIO
    if filename.endswith((".mp3", ".wav", ".aac")):
        return jsonify({"label": "Coming Soon", "confidence": 0})

    # 🔹 IMAGE PROCESSING
    file_type = request.form.get("type") or "image"

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    import time

    try:
        response = None

        # 🔁 RETRY LOGIC (clean)
        for attempt in range(3):
            try:
                with open(filepath, "rb") as f:
                    response = requests.post(
                        HF_API_URL, headers=HF_HEADERS, data=f.read(), timeout=30
                    )

                print(f"✅ HF success on attempt {attempt+1}")
                break

            except Exception as e:
                print(f"❌ Retry {attempt+1} failed:", e)
                time.sleep(2)

        # ❌ ALL FAILED
        if response is None:
            return jsonify({"label": "AI Error", "confidence": 0})

        data = response.json()

        # 🔥 HANDLE HF ERROR RESPONSE
        if isinstance(data, dict) and "error" in data:
            print("HF ERROR:", data)
            label = "Suspicious"
            confidence = 50

        else:
            result = data[0]

            confidence = int(result["score"] * 100)
            ai_label = result["label"].lower()

            if "fake" in ai_label:
                label = "Fake"
            elif "real" in ai_label:
                label = "Real"
            else:
                label = "Suspicious"

            # safety threshold
            if confidence < 60:
                label = "Suspicious"

            print("IMAGE AI:", result)

    except Exception as e:
        print("Image AI Error:", e)
        return jsonify({"label": "Unknown", "confidence": 0})

    # 🔹 SAVE TO DB
    conn = get_db()
    cur = conn.cursor()

    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    cur.execute(
        """
        INSERT INTO uploads (user_id, file_type, filename, result, confidence, date)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (session["user_id"], file_type, file.filename, label, confidence, date),
    )

    conn.commit()
    conn.close()

    return jsonify({"label": label, "confidence": confidence})


# ---------------- DELETE ----------------


@app.route("/delete_upload", methods=["POST"])
def delete_upload():

    if "user_id" not in session:
        return jsonify({"status": "error"})

    data = request.get_json()
    upload_id = data.get("id")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM uploads WHERE id=? AND user_id=?", (upload_id, session["user_id"])
    )

    conn.commit()
    conn.close()

    return jsonify({"status": "deleted"})


# -----------------logout--------------


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- RUN ----------------

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
