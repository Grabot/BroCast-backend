from redis import Redis
from app.config import DevelopmentConfig
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
socks = SocketIO(cors_allowed_origins="*")

# redis_conn = Redis(host=DevelopmentConfig.REDIS_URL, port=6379)
# r = redis_conn.pubsub()
REDIS_URL = "redis://%s:%s" % (DevelopmentConfig.REDIS_URL, DevelopmentConfig.REDIS_PORT)
print("redis url: %s" % REDIS_URL)


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    db.init_app(app)
    socks.init_app(app, message_queue=REDIS_URL)
    migrate.init_app(app, db)

    from app.rest import app_api as api_bp
    app.register_blueprint(api_bp)

    from app.sock import app_sock as sock_bp
    app.register_blueprint(sock_bp)

    from app import models

    return app
