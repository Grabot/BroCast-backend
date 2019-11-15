import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import app_home as home_bp
    app.register_blueprint(home_bp)

    return app


# from app.models import models

