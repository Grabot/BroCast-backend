from flask import Blueprint

app_api = Blueprint('api', __name__)

from app.rest import register
from app.rest import login
from app.rest import all
from app.rest import search
from app.rest import add
