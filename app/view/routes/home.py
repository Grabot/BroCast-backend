from app import db
from app.view.routes import app_view
from flask import render_template
from app.view.models.user import User


@app_view.route('/', methods=['GET', 'POST'])
@app_view.route('/home', methods=['GET', 'POST'])
def home():
    users = User.query.all()
    return render_template('home.html', users=users, title='Home')

