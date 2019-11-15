from flask import Blueprint

app_home = Blueprint('main', __name__)

from app.routes import home

