from app.view.routes import app_view
from flask import render_template
from app.view.models.bro import Bro
from app import db


@app_view.route('/bros', methods=['GET', 'POST'])
def bros():
    bro_list = Bro.query.all()
    return render_template('bros.html', bros=bro_list, title='Bros')


@app_view.route('/bros/nuke', methods=['GET', 'POST'])
def fresh_start():
    Bro.query.delete()
    db.session.commit()
    db.engine.execute('alter sequence Bro_id_seq RESTART with 1')
    return 'ok'

