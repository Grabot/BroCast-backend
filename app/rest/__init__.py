from flask import Blueprint

app_api = Blueprint('rest', __name__)

from app.rest import test
from app.rest import register
from app.rest import login
from app.rest import search

