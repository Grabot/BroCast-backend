from flask import Blueprint

app_sock = Blueprint('sock', __name__)

from app.sock import test
