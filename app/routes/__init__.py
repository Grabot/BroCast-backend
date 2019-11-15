from flask import Blueprint

app_home = Blueprint('main', __name__)

from app.routes import home
from app.routes import register
from app.routes import api_get
from app.routes import api_post

