import os
from dotenv import load_dotenv

# loads the environment variable file
load_dotenv()


class Config(object):
    POSTGRES_URL = os.environ["POSTGRES_URL"]
    POSTGRES_PORT = os.environ["POSTGRES_PORT"]
    POSTGRES_USER = os.environ["POSTGRES_USER"]
    POSTGRES_PW = os.environ["POSTGRES_PW"]
    POSTGRES_DB = os.environ["POSTGRES_DB"]

    DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}:{port}/{db}'.format(
        user=POSTGRES_USER, pw=POSTGRES_PW, url=POSTGRES_URL, port=POSTGRES_PORT, db=POSTGRES_DB)

    SQLALCHEMY_DATABASE_URI = DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True

