#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
from flask_migrate import Migrate
import os

# Set up database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# Initialize API
api = Api(app)

# -------------------- Resources --------------------

# Scientists Resource
class Scientists(Resource):
    def get(self):
        scientists = db.session.execute(db.select(Scientist)).scalars()
        scientists_list = [scientist.to_dict(rules=('-missions',)) for scientist in scientists]
        return make_response(jsonify(scientists_list), 200)

    def post(self):
        data = request.json

        # Validate input
        if not data.get("name") or not data.get("field_of_study"):
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

        try:
            new_scientist = Scientist(
                name=data["name"],
                field_of_study=data["field_of_study"]
            )
            db.session.add(new_scientist)
            db.session.commit()
            return make_response(jsonify(new_scientist.to_dict()), 201)
        except Exception:
            db.session.rollback()
            return make_response(jsonify({"errors": ["validation errors"]}), 500)


# ScientistById Resource
class ScientistById(Resource):
    def get(self, id):
        scientist = db.session.get(Scientist, id)
        if not scientist:
            return make_response(jsonify({"error": "Scientist not found"}), 404)

        # Serialize scientist with missions
        scientist_data = {
            "id": scientist.id,
            "name": scientist.name,
            "field_of_study": scientist.field_of_study,
            "missions": [
                {
                    "id": mission.id,
                    "name": mission.name,
                    "planet": {
                        "id": mission.planet.id,
                        "name": mission.planet.name,
                        "distance_from_earth": mission.planet.distance_from_earth,
                        "nearest_star": mission.planet.nearest_star
                    }
                }
                for mission in scientist.missions
            ]
        }
        return make_response(jsonify(scientist_data), 200)

    def patch(self, id):
        scientist = db.session.get(Scientist, id)
        if not scientist:
            return make_response(jsonify({"error": "Scientist not found"}), 404)

        data = request.json

        # Validate input
        if "name" in data and not data["name"]:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)
        if "field_of_study" in data and not data["field_of_study"]:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

        try:
            if "name" in data:
                scientist.name = data["name"]
            if "field_of_study" in data:
                scientist.field_of_study = data["field_of_study"]

            db.session.commit()
            return make_response(jsonify(scientist.to_dict()), 202)
        except Exception:
            db.session.rollback()
            return make_response(jsonify({"errors": ["validation errors"]}), 500)

    def delete(self, id):
        scientist = db.session.get(Scientist, id)
        if not scientist:
            return make_response(jsonify({"error": "Scientist not found"}), 404)

        try:
            db.session.delete(scientist)
            db.session.commit()
            return make_response(jsonify({}), 204)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [str(e)]}), 500)


# Planets Resource
class Planets(Resource):
    def get(self):
        try:
            planets = db.session.execute(db.select(Planet)).scalars()
            planets_list = [planet.to_dict() for planet in planets]
            return make_response(jsonify(planets_list), 200)
        except Exception as e:
            return make_response(jsonify({"errors": [str(e)]}), 500)


# Missions Resource
class Missions(Resource):
    def post(self):
        data = request.json

        # Validate input
        if not data.get('name') or not data.get('scientist_id') or not data.get('planet_id'):
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

        # Check if scientist and planet exist
        scientist = db.session.get(Scientist, data['scientist_id'])
        planet = db.session.get(Planet, data['planet_id'])
        if not scientist or not planet:
            return make_response(jsonify({"errors": ["Scientist or Planet not found."]}), 404)

        try:
            # Create and save the new mission
            mission = Mission(
                name=data['name'],
                scientist_id=scientist.id,
                planet_id=planet.id
            )
            db.session.add(mission)
            db.session.commit()

            # Return the mission details with 'planet' and 'scientist' keys
            return make_response(jsonify({
                "id": mission.id,
                "name": mission.name,
                "scientist_id": mission.scientist_id,
                "planet_id": mission.planet_id,
                "planet": {
                    "id": planet.id,
                    "name": planet.name,
                    "distance_from_earth": planet.distance_from_earth,
                    "nearest_star": planet.nearest_star
                },
                "scientist": {
                    "id": scientist.id,
                    "name": scientist.name,
                    "field_of_study": scientist.field_of_study
                }
            }), 201)

        except Exception:
            db.session.rollback()
            return make_response(jsonify({"errors": ["validation errors"]}), 400)


# -------------------- Register Resources --------------------
api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistById, '/scientists/<int:id>')
api.add_resource(Planets, '/planets')
api.add_resource(Missions, '/missions')


# Home Route
@app.route('/')
def home():
    return ''


# -------------------- Run the Application --------------------
if __name__ == '__main__':
    app.run(port=5555, debug=True)