import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)

    # add the routes
    from app.routes import app_home as home_bp
    app.register_blueprint(home_bp)
    from app.rest import app_api as api_bp
    app.register_blueprint(api_bp)

    # add the models
    from app import models

    return app

