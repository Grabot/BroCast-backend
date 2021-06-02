from app import db
from app.models.bro_bros import BroBros
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


def update_unread_messages(bro_id, bros_bro_id):
    # The other bro now gets an extra unread message
    other_bro_chat = BroBros.query.filter_by(bro_id=bros_bro_id, bros_bro_id=bro_id).first()

    # We assume this won't happen
    if other_bro_chat is None:
        return None

    other_bro_chat.update_unread_messages()
    other_bro_chat.update_last_activity()
    db.session.add(other_bro_chat)
    db.session.commit()
    return True
