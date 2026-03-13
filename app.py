# app.py
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, StudyData
from text_extractor import extract, organize_with_llm
from schedule_planner import generate_schedule

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "replace-with-a-secure-random-secret"  # change this
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///userdata.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db.init_app(app)

# ---------- helper ----------
def current_user_id():
    return session.get("user_id")

# ---------- routes ----------
@app.route("/")
def index():
    if current_user_id():
        return redirect(url_for("upload_page"))
    return render_template("login.html")

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return {"error": "username/password required"}, 400
    if User.query.filter_by(username=username).first():
        return {"error": "username exists"}, 400
    pw_hash = generate_password_hash(password)
    u = User(username=username, password_hash=pw_hash)
    db.session.add(u)
    db.session.commit()
    return {"message": "created"}, 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return {"error": "invalid credentials"}, 401
    session["user_id"] = user.id
    return {"message": "ok"}, 200

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("index"))

@app.route("/upload_page")
def upload_page():
    if not current_user_id():
        return redirect(url_for("index"))
    return render_template("Upload-page.html")

@app.route("/status")
def status_page():
    if not current_user_id():
        return redirect(url_for("index"))
    user_id = current_user_id()
    user_data = StudyData.query.filter_by(user_id=user_id).first()
    if not user_data or not user_data.extracted_json:
        return "Upload files first", 400
    data = json.loads(user_data.extracted_json)
    return render_template("Status.html", data=data)

@app.route("/schedule_page")
def schedule_page():
    if not current_user_id():
        return redirect(url_for("index"))
    return render_template("Schedule.html")

# File upload endpoint
@app.route("/upload", methods=["POST"])
def upload_files():
    if not current_user_id():
        return {"error": "unauthorized"}, 401
    user_id = current_user_id()
    files = request.files.getlist("files")
    if not files:
        return {"error":"no files"},400
    texts = []
    for f in files:
        filename = f.filename
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        f.save(save_path)
        texts.append(extract(save_path))
    # call the final LLM normalization
    today = datetime.utcnow().strftime("%Y-%m-%d")
    final_json = organize_with_llm(texts, today_date=today)
    # store into DB
    existing = StudyData.query.filter_by(user_id=user_id).first()
    if existing:
        existing.extracted_json = json.dumps(final_json)
    else:
        sd = StudyData(user_id=user_id, extracted_json=json.dumps(final_json))
        db.session.add(sd)
    db.session.commit()
    return jsonify(final_json)

@app.route("/subjects", methods=["GET"])
def get_subjects():
    if not current_user_id():
        return {"error":"unauthorized"},401
    user_id = current_user_id()
    ud = StudyData.query.filter_by(user_id=user_id).first()
    if not ud or not ud.extracted_json:
        return {"error":"no data"},404
    return jsonify(json.loads(ud.extracted_json))

@app.route("/submit_status", methods=["POST"])
def submit_status():
    if not current_user_id():
        return {"error":"unauthorized"},401
    user_id = current_user_id()
    payload = request.json
    ud = StudyData.query.filter_by(user_id=user_id).first()
    if not ud:
        ud = StudyData(user_id=user_id)
        db.session.add(ud)
    ud.topic_status = json.dumps(payload)
    db.session.commit()
    return {"message":"ok"},200

@app.route("/generate_schedule", methods=["POST"])
def generate():
    if not current_user_id():
        return {"error":"unauthorized"},401
    user_id = current_user_id()
    ud = StudyData.query.filter_by(user_id=user_id).first()
    if not ud or not ud.topic_status:
        return {"error":"no topic status"},400
    topic_data = json.loads(ud.topic_status)
    schedule = generate_schedule(topic_data)
    ud.schedule_json = json.dumps(schedule)
    db.session.commit()
    return jsonify(schedule)

@app.route("/schedule", methods=["GET"])
def get_schedule():
    if not current_user_id():
        return {"error":"unauthorized"},401
    user_id = current_user_id()
    ud = StudyData.query.filter_by(user_id=user_id).first()
    if not ud or not ud.schedule_json:
        return {"error":"no schedule"},404
    return jsonify(json.loads(ud.schedule_json))

# create db on first run
if __name__ == "__main__":
    with app.app_context():
        os.makedirs("instance", exist_ok=True)
        db.create_all()
    app.run(debug=True)