from app.view.routes import app_view
from flask import render_template
from app.view.models.bro import Bro


@app_view.route('/bros', methods=['GET', 'POST'])
def bros():
    bro_list = Bro.query.all()
    return render_template('bros.html', bros=bro_list, title='Bros')

