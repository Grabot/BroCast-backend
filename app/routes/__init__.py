from flask import Blueprint

app_view = Blueprint('main', __name__)

from app.routes import hello_world
