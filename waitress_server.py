from waitress import serve
import os
from src.app import create_app

env_name = os.getenv('FLASK_ENV')
app = create_app(env_name)
serve(app, host='0.0.0.0', port=8080)
