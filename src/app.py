from flask import Flask
import inspect
from .config import app_config
from .models import db, bcrypt
from .models.UserModel import UserSchema
from .models.LocationModel import LocationSchema
from .views.UserView import user_api as user_blueprint
from .views import UserView #UserView import create, login, get_all, get_a_user, get_me, update, delete
from .views import LocationView
from .views.LocationView import location_api as location_blueprint
from flasgger import Swagger, APISpec

# noinspection PyArgumentList

spec = APISpec(
    title='Location App',
    version='1.0.0',
    plugins=[
        'apispec.ext.flask',
        'apispec.ext.marshmallow'
    ]
)

def create_app(env_name):
    """
    Create the app
    """

    # app initialization
    app = Flask(__name__)
    app.config.from_object(app_config[env_name])

    # initializing bcrypt
    bcrypt.init_app(app)

    # initalizing db
    db.init_app(app)

    app.register_blueprint(user_blueprint, url_prefix='/api/v1/users')
    app.register_blueprint(location_blueprint, url_prefix='/api/v1/locations')

    template = spec.to_flasgger(
        app,
        definitions=[UserSchema, LocationSchema],
        paths=[UserView.create, UserView.get_all, UserView.get_me, UserView.get_a_user, UserView.update, UserView.delete, UserView.login,
               LocationView.create, LocationView.get_all, LocationView.get_between_dates, LocationView.update, LocationView.delete]
    )

    swag = Swagger(app, template=template)

    return app
