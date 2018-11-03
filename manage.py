import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from src.app import create_app, db

# we need to import the models here even though they are not explicitly used here, they are needed by Alembic when
# creating the migration
from src.models import UserModel, LocationModel


env_name = os.getenv('FLASK_ENV')
app = create_app(env_name)

migrate = Migrate(app=app, db=db)

manager = Manager(app=app)  # tracks all the commands and handles their call from command line

manager.add_command('db', MigrateCommand)   # MigrateCommand contains a set of migration commands
                                            # that can be called from command line

if __name__ == '__main__':
    manager.run()
    db.create_all()