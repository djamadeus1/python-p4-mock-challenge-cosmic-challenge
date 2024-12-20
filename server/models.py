from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    distance_from_earth = db.Column(db.Integer, nullable=False)
    nearest_star = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "distance_from_earth": self.distance_from_earth,
            "nearest_star": self.nearest_star
        }


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    field_of_study = db.Column(db.String, nullable=False)

    missions = db.relationship('Mission', backref='scientist', cascade="all, delete-orphan")
    serialize_rules = ('-missions.scientist',)

    @validates('name')
    def validate_name(self, key, value):
        if not value:
            raise ValueError("Scientist must have a name.")
        return value

    @validates('field_of_study')
    def validate_field_of_study(self, key, value):
        if not value:
            raise ValueError("Scientist must have a field of study.")
        return value


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)

    planet = db.relationship('Planet', backref='missions')

    @validates('name')
    def validate_name(self, key, value):
        if not value:
            raise ValueError("Mission must have a name.")
        return value

    @validates('scientist_id')
    def validate_scientist_id(self, key, value):
        if not value:
            raise ValueError("Mission must have a scientist_id.")
        return value

    @validates('planet_id')
    def validate_planet_id(self, key, value):
        if not value:
            raise ValueError("Mission must have a planet_id.")
        return value