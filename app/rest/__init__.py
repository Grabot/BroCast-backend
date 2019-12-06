from flask import Blueprint

app_api = Blueprint('rest', __name__)

from app.rest import register
from app.rest import login
from app.rest import search
from app.rest import add_bro
from app.rest import get_bros
from app.rest import get_message

