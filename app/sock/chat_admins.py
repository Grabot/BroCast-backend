from flask import request
from flask_socketio import emit
from app import db
from app.models.bro import Bro
from app.models.broup import Broup


def change_broup_add_admin(data):
    token = data["token"]
    broup_id = data["broup_id"]
    bro_id = data["bro_id"]
    logged_in_bro = Bro.verify_auth_token(token)

    if logged_in_bro is None:
        emit("message_event_change_broup_add_admin_failed", "token authentication failed", room=request.sid)
    else:
        broup_objects = Broup.query.filter_by(broup_id=broup_id)
        if broup_objects is None:
            emit("message_event_change_broup_add_admin_failed", "broup finding failed", room=request.sid)
        else:
            for broup in broup_objects:
                broup.add_admin(bro_id)
                db.session.add(broup)
                bro_room = "room_%s" % broup.bro_id
                emit("message_event_chat_changed", broup.serialize, room=bro_room)
            db.session.commit()


def change_broup_dismiss_admin(data):
    token = data["token"]
    broup_id = data["broup_id"]
    bro_id = data["bro_id"]
    logged_in_bro = Bro.verify_auth_token(token)

    if logged_in_bro is None:
        emit("message_event_change_broup_dismiss_admin_failed", "token authentication failed", room=request.sid)
    else:
        broup_objects = Broup.query.filter_by(broup_id=broup_id)
        if broup_objects is None:
            emit("message_event_change_broup_dismiss_admin_failed", "broup finding failed", room=request.sid)
        else:
            for broup in broup_objects:
                broup.dismiss_admin(bro_id)
                db.session.add(broup)
                bro_room = "room_%s" % broup.bro_id
                emit("message_event_chat_changed", broup.serialize, room=bro_room)
            db.session.commit()

