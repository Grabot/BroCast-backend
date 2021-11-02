from flask import Blueprint
from flask import render_template

app_api = Blueprint('api', __name__)

from app.rest import register
from app.rest import register_v1_1
from app.rest import login
from app.rest import login_v1_1
from app.rest import all
from app.rest import search
from app.rest import get_bros
from app.rest import get_messages
from app.rest import remove_registration
from app.rest import get_chat
from app.rest import block_bro
from app.rest import report_bro
from app.rest import remove_bro
from app.rest import read_logs
from app.rest import get_messages_broup
from app.rest import get_broup_bros
from app.rest import get_broup
from app.rest import report_broup


@app_api.route("/privacy")
def privacy():
    return render_template('privacy.html')


@app_api.route("/about")
def about():
    return render_template('about.html')


@app_api.route("/terms")
def terms():
    return render_template('terms.html')


@app_api.route("/")
def home():
    return render_template('index.html')
