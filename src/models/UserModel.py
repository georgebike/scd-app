from marshmallow import fields, Schema
from . import db
from . import bcrypt
from .LocationModel import LocationSchema

class UserModel(db.Model):
    """
    User Model
    """

    # table name
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_terminal = db.Column(db.Boolean, default=False, nullable=False)
    locations = db.relationship('LocationModel', backref='users', lazy=True)

    # class constructor
    def __init__(self, data):
        """
        Class constructor
        """

        self.username = data.get('username')
        self.password = self.__generate_hash(data.get('password'))
        self.is_terminal = data.get('is_terminal')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            if key == 'password':
                self.password = self.__generate_hash(item)
                item = self.password
            setattr(self, key, item)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __generate_hash(self, password):
        return bcrypt.generate_password_hash(password, rounds=10).decode("utf-8")

    def check_hash(self, password):
        return bcrypt.check_password_hash(self.password, password)

    @staticmethod
    def get_all_users():
        return UserModel.query.all()

    @staticmethod
    def get_one_user(id):
        return UserModel.query.get(id)

    @staticmethod
    def get_user_by_username(username):
        return UserModel.query.filter_by(username=username).first()

    def __repr__(self):
        return '<id {}>'.format(self.id)

class UserSchema(Schema):
    """
    Serialization of the UserModel
    """

    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    is_terminal = fields.Bool(required=True)
    locations = fields.Nested(LocationSchema, many=True)
