import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app.config import DevelopmentConfig
from app import create_app, db

app = create_app()
app.config.from_object(DevelopmentConfig)
print(app.config['SQLALCHEMY_DATABASE_URI'])
POSTGRES_URL = os.environ["POSTGRES_URL_LOCAL"]
POSTGRES_PORT = os.environ["POSTGRES_PORT"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PW = os.environ["POSTGRES_PW"]
POSTGRES_DB = os.environ["POSTGRES_DB"]

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}:{port}/{db}'.format(
    user=POSTGRES_USER, pw=POSTGRES_PW, url=POSTGRES_URL, port=POSTGRES_PORT, db=POSTGRES_DB)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
print(app.config['SQLALCHEMY_DATABASE_URI'])
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
