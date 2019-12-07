from app import db
from app.view.routes import app_view
from flask import render_template
from app.view.models.bro import Bro, BroBros, Message


@app_view.route('/test_functions', methods=['GET', 'POST'])
def test_functions():
    bros = Bro.query.all()
    for bro in bros:
        print("bro: " + bro.bro_name)
        print("has " + str(bro.bros.count()) + " bros right now")
        print("______________________________________________________")

    return "check logs"


@app_view.route('/clear_bros/<string:bro>/<string:bros_bro>', methods=['GET', 'POST'])
def clear_bros(bro, bros_bro):
    remove_bro = Bro.query.filter_by(bro_name=bro).first()
    to_be_removed_bro = Bro.query.filter_by(bro_name=bros_bro).first()
    remove_bro.remove_bro(to_be_removed_bro)
    db.session.commit()
    return "Bro %s no longer is a bro of %s" % (remove_bro.bro_name, to_be_removed_bro.bro_name)


@app_view.route('/messages/nuke', methods=['GET', 'POST'])
def clear_messages():
    Message.query.delete()
    db.session.commit()
    db.engine.execute('alter sequence message_id_seq RESTART with 1')
    return 'ok'


@app_view.route('/bros/nuke', methods=['GET', 'POST'])
def fresh_start():
    Bro.query.delete()
    db.session.commit()
    db.engine.execute('alter sequence bro_id_seq RESTART with 1')
    return 'ok'

