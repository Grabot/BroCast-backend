from flask import Blueprint

app_view = Blueprint('main', __name__)


from app.view.routes import home
from app.view.routes import bros
from app.view.routes import messages
from app.view.routes import register
from app.view.routes import test_functions

