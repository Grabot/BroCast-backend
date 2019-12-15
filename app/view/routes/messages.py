from app.view.routes import app_view
from app import db
from flask import render_template
from app.view.models.message import Message


@app_view.route('/messages', methods=['GET', 'POST'])
def messages():
    message_list = Message.query.all()
    return render_template('messages.html', messages=message_list, title='Messages')


@app_view.route('/messages/nuke', methods=['GET', 'POST'])
def clear_messages():
    Message.query.delete()
    db.session.commit()
    # db.engine.execute("alter sequence Message_id_seq RESTART with 1")
    return 'ok'

