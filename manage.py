# Here the database migration can be handled.
# A short example of how to update your database is as follows:
# make changes in a database model (User for example)
# locally execute the 'python manage.py db migrate' command
# This adds a python script in the 'migrations/versions' folder
# locally execute the 'python manage.py db upgrade' command to update the database with the changes
# commit all the changes including the migration folder
# execute on your server the 'python manage.py db upgrade' command.
# You only need the upgrade command because the change is in the migration folder.
import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app, db


app.config.from_object(os.environ['APP_SETTINGS'])

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()

