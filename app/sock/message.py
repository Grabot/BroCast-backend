from datetime import datetime
from flask import request
from app import db
from app.models.bro_bros import BroBros
from app.models.broup import Broup
from app.models.broup_message import BroupMessage
from app.models.message import Message
from app.sock.notification import send_notification
from app.sock.notification import send_notification_broup
from app.models.bro import get_a_room_you_two
from flask_socketio import emit
from app.sock.update import update_broups


def send_message(data):
    print("sending message")
    bro_id = data["bro_id"]
    bros_bro_id = data["bros_bro_id"]
    message = data["message"]
    text_message = data["text_message"]

    own_chat = BroBros.query.filter_by(bro_id=bro_id, bros_bro_id=bros_bro_id).first()
    other_bro_chat = BroBros.query.filter_by(bro_id=bros_bro_id, bros_bro_id=bro_id).first()

    # We assume this won't happen
    if own_chat is None:
        return None

    bro_message = Message(
        sender_id=bro_id,
        recipient_id=bros_bro_id,
        body=message,
        text_message=text_message,
        timestamp=datetime.utcnow(),
        info=False
    )

    if other_bro_chat is not None and not other_bro_chat.is_blocked():
        print("we should send notification")
        print(data)
        send_notification(data)
        # The other bro now gets an extra unread message
        other_bro_chat.update_unread_messages()
        other_bro_chat.update_last_activity()
        other_bro_chat.check_mute()
        db.session.add(other_bro_chat)

        # We only have to update the other bro's chat.
        room_bro_2 = "room_%s" % bros_bro_id
        emit("message_event_chat_changed", other_bro_chat.serialize, room=room_bro_2)

    # We update the activity on our own chat object as well
    own_chat.update_last_activity()
    # We send the message so we've obviously read it as well.
    # own_chat.update_last_message_read_time_bro()

    own_chat.check_mute()
    db.session.add(own_chat)
    db.session.add(bro_message)
    db.session.commit()

    # We do it after saving so the message will have it's id.
    if other_bro_chat is not None and not other_bro_chat.is_blocked():
        room = get_a_room_you_two(bro_id, bros_bro_id)
        emit("message_event_send", bro_message.serialize, room=room)
    else:
        # If the user is blocked or reported we don't want to send an update to the other bro.
        own_room = "room_%s" % bro_id
        emit("message_event_send", bro_message.serialize, room=own_room)


def send_message_broup(data):
    bro_id = data["bro_id"]
    broup_id = data["broup_id"]
    message = data["message"]
    text_message = data["text_message"]

    broup_message = BroupMessage(
        sender_id=bro_id,
        broup_id=broup_id,
        body=message,
        text_message=text_message,
        timestamp=datetime.utcnow(),
        info=False
    )

    broup_objects = Broup.query.filter_by(broup_id=broup_id)
    bro_ids = []
    if broup_objects is None:
        emit("message_event_send_broup", "broup finding failed", room=request.sid)
    else:
        for broup in broup_objects:
            if broup.bro_id == bro_id:
                # The bro that send the message obviously also read it.
                broup.update_last_message_read_time_bro()

                bro_ids = broup.get_participants()
            else:
                # The other bro's now gets an extra unread message and their chat is moved to the top of their list.
                broup.update_unread_messages()

            broup.update_last_activity()
            broup.check_mute()
            db.session.add(broup)

    db.session.add(broup_message)
    db.session.commit()

    update_broups(broup_objects)

    send_notification_broup(bro_ids, message, broup_id, broup_objects, bro_id)
    broup_room = "broup_%s" % broup_id
    emit("message_event_send", broup_message.serialize, room=broup_room)

