from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from text_extractor import extract, organize_with_llm
from schedule_planner import generate_schedule
import json
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# -----------------------
# DATABASE
# -----------------------

class StudyData(db.Model):

    userid = db.Column(db.Integer, primary_key=True)

    extracted_json = db.Column(db.Text)

    topic_status = db.Column(db.Text)

    schedule_json = db.Column(db.Text)


# -----------------------
# PAGE ROUTES
# -----------------------

@app.route("/")
def upload_page():
    return render_template("Upload-page.html")


@app.route("/status")
def status_page():

    userid = 1

    user = StudyData.query.filter_by(userid=userid).first()

    if not user:
        return "Upload files first"

    data = json.loads(user.extracted_json)

    dates = []

    for s in data["subjects"]:
        if s.get("exam_date"):
            dates.append(s["exam_date"])

    return render_template(
        "Status.html",
        data=data,
        dates=dates
    )


@app.route("/schedule_page")
def schedule_page():
    return render_template("Schedule.html")


# -----------------------
# FILE UPLOAD
# -----------------------

@app.route("/upload", methods=["POST"])
def upload_files():

    userid = request.form.get("userid")

    files = request.files.getlist("files")

    all_text = []

    for file in files:

        path = "uploads/" + file.filename

        file.save(path)

        text = extract(path)

        all_text.append(text)

    final_json = organize_with_llm(all_text)

    existing = StudyData.query.filter_by(userid=userid).first()

    if existing:

        existing.extracted_json = json.dumps(final_json)

    else:

        new = StudyData(
            userid=userid,
            extracted_json=json.dumps(final_json)
        )

        db.session.add(new)

    db.session.commit()

    return jsonify(final_json)

# -----------------------
# SAVE STATUS
# -----------------------

@app.route("/submit_status/<int:userid>", methods=["POST"])
def submit_status(userid):

    user = StudyData.query.filter_by(userid=userid).first()

    if not user:
        return {"error": "User not found"},404

    user.topic_status = json.dumps(request.json)

    db.session.commit()

    return {"message":"saved"}


# -----------------------
# GENERATE SCHEDULE
# -----------------------

@app.route("/generate_schedule/<int:userid>", methods=["POST"])
def generate(userid):

    user = StudyData.query.filter_by(userid=userid).first()

    topic_data = json.loads(user.topic_status)

    schedule = generate_schedule(topic_data)

    user.schedule_json = json.dumps(schedule)

    db.session.commit()

    return jsonify(schedule)


# -----------------------
# GET FINAL SCHEDULE
# -----------------------

@app.route("/schedule/<int:userid>")
def schedule(userid):

    user = StudyData.query.filter_by(userid=userid).first()

    if not user:
        return {"error":"not found"}

    return jsonify(json.loads(user.schedule_json))


# -----------------------

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)