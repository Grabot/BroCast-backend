from app import db
from app.models.message import Message


def send_message(data):
    bro_id = data["bro_id"]
    bros_bro_id = data["bros_bro_id"]
    message = data["message"]
    text_message = data["text_message"]

    bro_message = Message(
        sender_id=bro_id,
        recipient_id=bros_bro_id,
        body=message,
        text_message=text_message
    )

    db.session.add(bro_message)
    db.session.commit()
    return bro_message

