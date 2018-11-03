from marshmallow import fields, Schema
from . import db
import datetime

class LocationModel(db.Model):
    """
    Location Model
    """

    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    info = db.Column(db.String(250), nullable=True)
    posted_at = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key from Users

    def __init__(self, data):
        self.latitude = data.get('latitude')
        self.longitude = data.get('longitude')
        self.info = data.get('info')
        self.owner_id = data.get('owner_id')
        self.posted_at = datetime.datetime.utcnow()


    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        self.posted_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_locations():
        return LocationModel.query.all()

    @staticmethod
    def get_one_location(id):
        return LocationModel.query.get(id)

    @staticmethod
    def get_by_dates(start_date, end_date):
        return LocationModel.query.filter(LocationModel.posted_at.between(start_date, end_date))

    def __repr__(self):
        return '<id {}>'.format(self.id)

class LocationSchema(Schema):
    id = fields.Int(dump_only=True)
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    info = fields.Str(required=True)
    owner_id = fields.Int(required=True)
    posted_at = fields.DateTime(dump_only=True)