import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app.config import Config
from app import create_app, db

app = create_app()
app.config.from_object(Config)
# POSTGRES = {
#     'user': os.environ.get('POSTRGES_USER'),
#     'pw': os.environ.get('POSTGRES_PASSWORD'),
#     'db': os.environ.get('POSTGRES_DATABASE'),
#     'host': os.environ.get('POSTGRES_HOST'),
#     'port': os.environ.get('POSTGRES_PORT')
# }
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
# When running flask migrations on the database the connection should explicitly be set here
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()