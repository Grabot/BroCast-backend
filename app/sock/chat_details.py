from flask import request
from flask_socketio import emit
from app.models.bro import Bro, get_a_room_you_two
from app.models.bro_bros import BroBros
from app import db
from app.models.broup import Broup


def change_chat_details(data):
    token = data["token"]
    bros_bro_id = data["bros_bro_id"]
    description = data["description"]
    logged_in_bro = Bro.verify_auth_token(token)

    if logged_in_bro is None:
        emit("message_event_change_chat_details_failed", "token authentication failed", room=request.sid)
    else:
        chat1 = BroBros.query.filter_by(bro_id=logged_in_bro.id, bros_bro_id=bros_bro_id).first()
        chat2 = BroBros.query.filter_by(bro_id=bros_bro_id, bros_bro_id=logged_in_bro.id).first()
        if chat1 is None or chat2 is None:
            emit("message_event_change_chat_details_failed", "chat finding failed", room=request.sid)
        else:
            chat1.update_description(description)
            db.session.add(chat1)
            chat2.update_description(description)
            db.session.add(chat2)
            db.session.commit()
            room = get_a_room_you_two(logged_in_bro.id, bros_bro_id)
            emit("message_event_change_chat_details_success",
                 {
                     "result": True,
                     "description": description
                 }, room=room)


def change_chat_alias(data):
    token = data["token"]
    bros_bro_id = data["bros_bro_id"]
    alias = data["alias"]
    logged_in_bro = Bro.verify_auth_token(token)
    print("updating alias for chat")
    if logged_in_bro is None:
        emit("message_event_change_chat_alias_failed", "token authentication failed", room=request.sid)
    else:
        chat1 = BroBros.query.filter_by(bro_id=logged_in_bro.id, bros_bro_id=bros_bro_id).first()
        if chat1 is None:
            emit("message_event_change_chat_alias_failed", "chat finding failed", room=request.sid)
        else:
            chat1.update_alias(alias)
            db.session.add(chat1)
            db.session.commit()
            emit("message_event_change_chat_alias_success", "chat updated successfully", room=request.sid)


def change_chat_colour(data):
    token = data["token"]
    bros_bro_id = data["bros_bro_id"]
    colour = data["colour"]
    logged_in_bro = Bro.verify_auth_token(token)

    if logged_in_bro is None:
        emit("message_event_change_chat_colour_failed", "token authentication failed", room=request.sid)
    else:
        chat1 = BroBros.query.filter_by(bro_id=logged_in_bro.id, bros_bro_id=bros_bro_id).first()
        chat2 = BroBros.query.filter_by(bro_id=bros_bro_id, bros_bro_id=logged_in_bro.id).first()
        if chat1 is None or chat2 is None:
            emit("message_event_change_chat_colour_failed", "chat colour change failed", room=request.sid)
        else:
            chat1.update_colour(colour)
            db.session.add(chat1)
            chat2.update_colour(colour)
            db.session.add(chat2)
            db.session.commit()
            room = get_a_room_you_two(logged_in_bro.id, bros_bro_id)
            emit("message_event_change_chat_colour_success",
                 {
                     "result": True,
                     "colour": colour
                 }, room=room)


def change_broup_details(data):
    token = data["token"]
    broup_id = data["broup_id"]
    description = data["description"]
    logged_in_bro = Bro.verify_auth_token(token)

    if logged_in_bro is None:
        emit("message_event_change_broup_details_failed", "token authentication failed", room=request.sid)
    else:
        broup_objects = Broup.query.filter_by(broup_id=broup_id)
        if broup_objects is None:
            emit("message_event_change_broup_details_failed", "broup finding failed", room=request.sid)
        else:
            for broup in broup_objects:
                broup.update_description(description)
                db.session.add(broup)
            db.session.commit()
            broup_room = "broup_%s" % broup_id
            emit("message_event_change_broup_details_success",
                 {
                     "result": True,
                     "description": description
                 }, room=broup_room)


def change_broup_alias(data):
    token = data["token"]
    broup_id = data["broup_id"]
    alias = data["alias"]
    logged_in_bro = Bro.verify_auth_token(token)

    if logged_in_bro is None:
        emit("message_event_change_broup_alias_failed", "token authentication failed", room=request.sid)
    else:
        broup = Broup.query.filter_by(broup_id=broup_id, bro_id=logged_in_bro.id).first()
        if broup is None:
            emit("message_event_change_broup_alias_failed", "broup finding failed", room=request.sid)
        else:
            broup.update_alias(alias)
            db.session.add(broup)
            db.session.commit()
            emit("message_event_change_broup_alias_success", "broup updated successfully", room=request.sid)


def change_broup_colour(data):
    token = data["token"]
    broup_id = data["broup_id"]
    colour = data["colour"]
    logged_in_bro = Bro.verify_auth_token(token)

    if logged_in_bro is None:
        emit("message_event_change_broup_colour_failed", "token authentication failed", room=request.sid)
    else:
        broup_objects = Broup.query.filter_by(broup_id=broup_id)
        if broup_objects is None:
            emit("message_event_change_broup_details_failed", "broup finding failed", room=request.sid)
        else:
            for broup in broup_objects:
                broup.update_colour(colour)
                db.session.add(broup)
            db.session.commit()
            broup_room = "broup_%s" % broup_id
            emit("message_event_change_broup_colour_success",
                 {
                     "result": True,
                     "colour": colour
                 }, room=broup_room)

