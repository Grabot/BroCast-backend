import os
from dotenv import load_dotenv

# loads the environment variable file
load_dotenv()


class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ["SECRET_KEY"]
    NOTIFICATION_KEY = os.environ["NOTIFICATION_KEY"]
    LOG_READ_PASSWORD = os.environ["LOG_READ_PASSWORD"]
    FIREBASE_URL = "https://fcm.googleapis.com/fcm/send"
    DEBUG = True


class DevelopmentConfig(Config):
    POSTGRES_URL = os.environ["POSTGRES_URL"]
    POSTGRES_PORT = os.environ["POSTGRES_PORT"]
    POSTGRES_USER = os.environ["POSTGRES_USER"]
    POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
    POSTGRES_DB = os.environ["POSTGRES_DB"]

    REDIS_URL = os.environ["REDIS_URL"]
    REDIS_PORT = os.environ["REDIS_PORT"]

    DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}:{port}/{db}'.format(
        user=POSTGRES_USER, pw=POSTGRES_PASSWORD, url=POSTGRES_URL, port=POSTGRES_PORT, db=POSTGRES_DB)

    REDIS_URL = "redis://{url}:{port}".format(url=REDIS_URL, port=REDIS_PORT)

    SQLALCHEMY_DATABASE_URI = DB_URL

