from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    print("is it going to print this?")
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://test:test@db/test"
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import app_view as home_bp
    app.register_blueprint(home_bp)

    return app
