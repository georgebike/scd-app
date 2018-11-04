import os
from src.app import create_app


if __name__ == '__main__':
    env_name = os.getenv('FLASK_ENV')   # get the environment (development/production) from env variables)
    print(env_name)
    app = create_app(env_name)          # create the app with the corresponding environment
    port = os.getenv('PORT')
    app.run(host='0.0.0.0', port=8080)                           # run the app
