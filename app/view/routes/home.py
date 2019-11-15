from app.view.routes import app_view
from flask import render_template


@app_view.route('/', methods=['GET', 'POST'])
@app_view.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html', title='Home')

