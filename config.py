import os


class Config(object):
    """
    Here the configuration of the application are given. Some examples are the database url and the secret key.
    """
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://localhost/brocast'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_Key = os.environ.get('FIREBASE_API_KEY') or 'fill in api key'


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/brocasttest'


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

