from datetime import datetime
from flask import request
from flask_socketio import emit
from app import db
from app.models.bro import Bro
from app.models.broup import Broup
from app.models.broup_message import BroupMessage
from app.sock.update import update_broups


def change_broup_add_admin(data):
    token = data["token"]
    broup_id = data["broup_id"]
    bro_id = data["bro_id"]
    logged_in_bro = Bro.verify_auth_token(token)
    new_admin_bro = Bro.query.filter_by(id=bro_id).first()

    if logged_in_bro is None or new_admin_bro is None:
        emit("message_event_change_broup_add_admin_failed", "token authentication failed", room=request.sid)
    else:
        broup_objects = Broup.query.filter_by(broup_id=broup_id)
        if broup_objects is None:
            emit("message_event_change_broup_add_admin_failed", "broup finding failed", room=request.sid)
        else:
            for broup in broup_objects:
                broup.add_admin(bro_id)
                db.session.add(broup)
            db.session.commit()

            # We create an info message with the person who is admin as sender (even if they didn't send the update)
            broup_message = BroupMessage(
                sender_id=bro_id,
                broup_id=broup_id,
                body="%s has been made admin" % new_admin_bro.get_full_name(),
                text_message="",
                timestamp=datetime.utcnow(),
                info=True
            )
            db.session.add(broup_message)
            db.session.commit()
            update_broups(broup_objects)

            broup_room = "broup_%s" % broup_id
            emit("message_event_send", broup_message.serialize, room=broup_room)


def change_broup_dismiss_admin(data):
    token = data["token"]
    broup_id = data["broup_id"]
    bro_id = data["bro_id"]
    logged_in_bro = Bro.verify_auth_token(token)
    old_admin_bro = Bro.query.filter_by(id=bro_id).first()

    if logged_in_bro is None or old_admin_bro is None:
        emit("message_event_change_broup_dismiss_admin_failed", "token authentication failed", room=request.sid)
    else:
        broup_objects = Broup.query.filter_by(broup_id=broup_id)
        if broup_objects is None:
            emit("message_event_change_broup_dismiss_admin_failed", "broup finding failed", room=request.sid)
        else:
            for broup in broup_objects:
                broup.dismiss_admin(bro_id)
                db.session.add(broup)

            # We create an info message with the person who is admin as sender (even if they didn't send the update)
            broup_message = BroupMessage(
                sender_id=bro_id,
                broup_id=broup_id,
                body="%s is no longer admin" % old_admin_bro.get_full_name(),
                text_message="",
                timestamp=datetime.utcnow(),
                info=True
            )
            db.session.add(broup_message)
            db.session.commit()
            update_broups(broup_objects)

            broup_room = "broup_%s" % broup_id
            emit("message_event_send", broup_message.serialize, room=broup_room)

