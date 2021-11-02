from datetime import datetime
from flask import request
from app import db
from app.models.bro_bros import BroBros
from app.models.broup import Broup
from app.models.broup_message import BroupMessage
from app.models.message import Message
from app.rest.notification import send_notification
from app.rest.notification import send_notification_broup
from app.models.bro import get_a_room_you_two
from flask_socketio import emit


def send_message(data):
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
        timestamp=datetime.utcnow()
    )

    if other_bro_chat is not None and not other_bro_chat.is_blocked():
        send_notification(data)
        # The other bro now gets an extra unread message
        other_bro_chat.update_unread_messages()
        other_bro_chat.update_last_activity()
        db.session.add(other_bro_chat)

        room = get_a_room_you_two(bro_id, bros_bro_id)
        emit("message_event_send", bro_message.serialize, room=room)
        room_solo_other_bro = "room_%s" % bros_bro_id
        emit("message_event_send_solo", bro_message.serialize, room=room_solo_other_bro)
    else:
        # If the user is blocked or reported we don't want to send an update to the other bro.
        own_room = "room_%s" % bro_id
        emit("message_event_send", bro_message.serialize, room=own_room)

    # We update the activity on our own chat object as well
    own_chat.update_last_activity()

    db.session.add(own_chat)
    db.session.add(bro_message)
    db.session.commit()


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
        timestamp=datetime.utcnow()
    )

    broup_objects = Broup.query.filter_by(broup_id=broup_id)
    if broup_objects is None:
        emit("message_event_send_broup", "broup finding failed", room=request.sid)
    else:
        bro_ids = []
        chat = ""
        for broup in broup_objects:
            if broup.bro_id == bro_id:
                # The bro that send the message obviously also read it.
                read_time = datetime.utcnow()
                broup.update_last_message_read_time_bro(read_time)
                # This should be the same for all broup objects
                bro_ids = broup.get_participants()
                chat = broup.serialize
            else:
                # The other bro's now gets an extra unread message and their chat is moved to the top of their list.
                broup.update_unread_messages()

            broup.update_last_activity()
            db.session.add(broup)

        send_notification_broup(bro_ids, message, chat)
        broup_room = "broup_%s" % broup_id
        emit("message_event_send", broup_message.serialize, room=broup_room)
        print("sending notification via socket to all bro's")
        for other_bro_id in bro_ids:
            if other_bro_id != bro_id:
                solo_room = "room_%s" % other_bro_id
                print("sending broup update to room %s" % solo_room)
                emit("message_event_send_solo", broup_message.serialize, room=solo_room)

    db.session.add(broup_message)
    db.session.commit()
    print("message is send in broup. Send sock notification")
