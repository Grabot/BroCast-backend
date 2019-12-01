import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


app = Flask(__name__)
app.config.from_object(Config)
POSTGRES = {
    'user': os.environ.get('POSTRGES_USER'),
    'pw': os.environ.get('POSTGRES_PASSWORD'),
    'db': os.environ.get('POSTGRES_DATABASE'),
    'host': os.environ.get('POSTGRES_HOST'),
    'port': os.environ.get('POSTGRES_PORT')
}
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

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


# db = SQLAlchemy()
# migrate = Migrate()
#
# def create_app(config_class=Config):
#     app = Flask(__name__)
#     app.config.from_object(Config)
#     db.init_app(app)
#     migrate.init_app(app, db)
#
#     # add the routes
#     from app.view.routes import app_view as home_bp
#     app.register_blueprint(home_bp)
#     from app.rest import app_api as api_bp
#     app.register_blueprint(api_bp)
#
#     # add the models
#     from app.view import models
#
#     return app
#
