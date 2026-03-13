from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from text_extractor import extract
from schedule_planner import generate_schedule
import json

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)


# -----------------------
# DATABASE MODEL
# -----------------------

class StudyData(db.Model):

    userid = db.Column(db.Integer, primary_key=True)

    extracted_json = db.Column(db.Text)

    topic_status = db.Column(db.Text)

    schedule_json = db.Column(db.Text)


# -----------------------
# UPLOAD FILES
# -----------------------

@app.route("/upload", methods=["POST"])
def upload_files():

    userid = request.form.get("userid")

    files = request.files.getlist("files")

    all_subjects = []

    for file in files:

        path = "uploads/" + file.filename

        file.save(path)

        result = extract(path)

        if "subjects" in result:
            all_subjects.extend(result["subjects"])

    data = {
        "subjects": all_subjects
    }

    existing = StudyData.query.filter_by(userid=userid).first()

    if existing:

        existing.extracted_json = json.dumps(data)

    else:

        new = StudyData(
            userid=userid,
            extracted_json=json.dumps(data)
        )

        db.session.add(new)

    db.session.commit()

    return jsonify(data)


# -----------------------
# GET EXTRACTED DATA
# -----------------------

@app.route("/subjects/<int:userid>", methods=["GET"])
def get_subjects(userid):

    user = StudyData.query.filter_by(userid=userid).first()

    if not user:
        return {"error":"User not found"},404

    return jsonify(json.loads(user.extracted_json))


# -----------------------
# SUBMIT TOPIC STATUS
# -----------------------

@app.route("/submit_status/<int:userid>", methods=["POST"])
def submit_status(userid):

    data = request.json

    user = StudyData.query.filter_by(userid=userid).first()

    if not user:
        return {"error":"User not found"},404

    user.topic_status = json.dumps(data)

    db.session.commit()

    return {"message":"Status saved"}


# -----------------------
# GENERATE SCHEDULE
# -----------------------

@app.route("/generate_schedule/<int:userid>", methods=["POST"])
def generate(userid):

    user = StudyData.query.filter_by(userid=userid).first()

    if not user:
        return {"error":"User not found"},404

    topic_data = json.loads(user.topic_status)

    schedule = generate_schedule(topic_data)

    user.schedule_json = json.dumps(schedule)

    db.session.commit()

    return jsonify(schedule)


# -----------------------
# GET FINAL SCHEDULE
# -----------------------

@app.route("/schedule/<int:userid>", methods=["GET"])
def get_schedule(userid):

    user = StudyData.query.filter_by(userid=userid).first()

    if not user:
        return {"error":"User not found"},404

    return jsonify(json.loads(user.schedule_json))


# -----------------------
# MAIN
# -----------------------

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)