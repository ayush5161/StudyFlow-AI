from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse
from text_extractor import extract_schedule
import json

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)


class Schedule(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    datesheet = db.Column(db.String(8000), nullable=False)
    topics = db.Column(db.String(8000), nullable=False)

    def __repr__(self):
        return f"Schedule(userid={self.userid})"


parser = reqparse.RequestParser()
parser.add_argument('datesheet', type=str, required=True, help="Datesheet is required")
parser.add_argument('topics', type=str, required=True, help="Topics are required")


class Item(Resource):

    def get(self, userid):
        item = Schedule.query.filter_by(userid=userid).first()

        if item:
            return {
                "userid": item.userid,
                "datesheet": item.datesheet,
                "topics": item.topics
            }, 200

        return {"message": "Item not found"}, 404


    def post(self, userid):

        if Schedule.query.filter_by(userid=userid).first():
            return {"message": f"User '{userid}' already exists"}, 400

        data = parser.parse_args()

        item = Schedule(
            userid=userid,
            datesheet=data["datesheet"],
            topics=data["topics"]
        )

        db.session.add(item)
        db.session.commit()

        return {
            "userid": item.userid,
            "datesheet": item.datesheet,
            "topics": item.topics
        }, 201


    def delete(self, userid):

        item = Schedule.query.filter_by(userid=userid).first()

        if item:
            db.session.delete(item)
            db.session.commit()
            return {"message": "Item deleted"}, 200

        return {"message": "Item not found"}, 404


    def put(self, userid):

        data = parser.parse_args()

        item = Schedule.query.filter_by(userid=userid).first()

        if item:
            item.datesheet = data["datesheet"]
            item.topics = data["topics"]

        else:
            item = Schedule(
                userid=userid,
                datesheet=data["datesheet"],
                topics=data["topics"]
            )
            db.session.add(item)

        db.session.commit()

        return {
            "userid": item.userid,
            "datesheet": item.datesheet,
            "topics": item.topics
        }, 200


class ItemList(Resource):

    def get(self):

        items = Schedule.query.all()

        return [
            {
                "userid": item.userid,
                "datesheet": item.datesheet,
                "topics": item.topics
            }
            for item in items
        ], 200


api.add_resource(ItemList, '/item')
api.add_resource(Item, '/item/<int:userid>')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)