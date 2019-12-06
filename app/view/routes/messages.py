from app.view.routes import app_view
from flask import render_template
from app.view.models.message import Message


@app_view.route('/messages', methods=['GET', 'POST'])
def messages():
    message_list = Message.query.all()
    return render_template('messages.html', messages=message_list, title='Messages')

