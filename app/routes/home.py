from app.routes import app_home
from flask import render_template


@app_home.route('/', methods=['GET', 'POST'])
@app_home.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html', title='Home')

