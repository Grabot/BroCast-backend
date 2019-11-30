from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


app = Flask(__name__)
app.config.from_object(Config)
POSTGRES = {
    'user': 'brocastadmin',
    'pw': 'rps4nvuh4g5d2r1j',
    'db': 'brocastdb',
    'host': 'brocast-1.cg9fwmgrjypi.eu-central-1.rds.amazonaws.com',
    'port': '5432',
}
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

# add the routes
from app.view.routes import app_view as home_bp
app.register_blueprint(home_bp)
from app.rest import app_api as api_bp
app.register_blueprint(api_bp)

# add the models
from app.view import models


