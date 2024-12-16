#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''


# GET /scientists - List all scientists
@app.route('/scientists', methods=['GET'])
def get_scientists():
    scientists = Scientist.query.all()
    scientists_data = [
        {
            "id": scientist.id,
            "name": scientist.name,
            "field_of_study": scientist.field_of_study
        }
        for scientist in scientists
    ]
    return jsonify(scientists_data)


# GET /scientists/<int:id> - Get a scientist by ID and include missions
@app.route('/scientists/<int:id>', methods=['GET'])
def get_scientist_by_id(id):
    scientist = db.session.get(Scientist, id)

    if scientist:
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
                        "nearest_star": mission.planet.nearest_star,
                    }
                }
                for mission in scientist.missions
            ]
        }
        return jsonify(scientist_data)
    else:
        return jsonify({"error": "Scientist not found"}), 404


# POST /scientists - Create a new scientist
@app.route('/scientists', methods=['POST'])
def create_scientist():
    data = request.get_json()

    if not data.get("name") or not data.get("field_of_study"):
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        new_scientist = Scientist(
            name=data["name"],
            field_of_study=data["field_of_study"]
        )
        db.session.add(new_scientist)
        db.session.commit()
        return jsonify({
            "id": new_scientist.id,
            "name": new_scientist.name,
            "field_of_study": new_scientist.field_of_study
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 500


# PATCH /scientists/<int:id> - Update an existing scientist
@app.route('/scientists/<int:id>', methods=['PATCH'])
def update_scientist(id):
    scientist = db.session.get(Scientist, id)
    if not scientist:
        return jsonify({"error": "Scientist not found"}), 404

    data = request.get_json()
    if "name" in data and not data["name"].strip():
        return jsonify({"errors": ["validation errors"]}), 400
    if "field_of_study" in data and not data["field_of_study"].strip():
        return jsonify({"errors": ["validation errors"]}), 400

    if "name" in data:
        scientist.name = data["name"]
    if "field_of_study" in data:
        scientist.field_of_study = data["field_of_study"]

    try:
        db.session.commit()
        return jsonify({
            "id": scientist.id,
            "name": scientist.name,
            "field_of_study": scientist.field_of_study
        }), 202
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 500


# DELETE /scientists/<int:id> - Delete a scientist
@app.route('/scientists/<int:id>', methods=['DELETE'])
def delete_scientist(id):
    scientist = db.session.get(Scientist, id)
    if not scientist:
        return jsonify({"error": "Scientist not found"}), 404

    try:
        db.session.delete(scientist)
        db.session.commit()
        response = make_response(jsonify({}), 204)
        response.headers["Content-Type"] = "application/json"
        return response
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 500


# GET /planets - List all planets
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planets_data = [
        {
            "id": planet.id,
            "name": planet.name,
            "distance_from_earth": planet.distance_from_earth,
            "nearest_star": planet.nearest_star
        }
        for planet in planets
    ]
    return jsonify(planets_data)


# POST /missions - Create a new mission
@app.route('/missions', methods=['POST'])
def create_mission():
    data = request.get_json()

    if not data.get('name') or not data.get('scientist_id') or not data.get('planet_id'):
        return jsonify({"errors": ["validation errors"]}), 400

    scientist = db.session.get(Scientist, data["scientist_id"])
    planet = db.session.get(Planet, data["planet_id"])

    if not scientist or not planet:
        return jsonify({"errors": ["Scientist or Planet not found."]}), 404

    try:
        new_mission = Mission(
            name=data["name"],
            scientist_id=scientist.id,
            planet_id=planet.id
        )
        db.session.add(new_mission)
        db.session.commit()
        mission_data = {
            "id": new_mission.id,
            "name": new_mission.name,
            "scientist_id": new_mission.scientist_id,
            "planet_id": new_mission.planet_id,
            "scientist": {
                "id": scientist.id,
                "name": scientist.name,
                "field_of_study": scientist.field_of_study
            },
            "planet": {
                "id": planet.id,
                "name": planet.name,
                "distance_from_earth": planet.distance_from_earth,
                "nearest_star": planet.nearest_star
            }
        }
        return jsonify(mission_data), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 500


if __name__ == '__main__':
    app.run(port=5555, debug=True)

    
    