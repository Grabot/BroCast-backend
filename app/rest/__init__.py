from flask import Blueprint

app_api = Blueprint('rest', __name__)

from app.rest import test

