from flask import request
from flask_socketio import emit
from app.models.bro import Bro
from app.models.bro_bros import BroBros
from app import db
from datetime import datetime, timedelta
from app.models.broup import Broup
from app.models.broup_message import BroupMessage
from app.models.message import Message
from app.models.bro import get_a_room_you_two
from app.util.util import remove_last_occur, update_broups


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
            room_bro_1 = "room_%s" % logged_in_bro.id
            room_bro_2 = "room_%s" % bros_bro_id
            emit("message_event_chat_changed", chat1.serialize, room=room_bro_1)
            emit("message_event_chat_changed", chat2.serialize, room=room_bro_2)

            # We create an info message with the person who did the update as sender
            bro_message = Message(
                sender_id=logged_in_bro.id,
                recipient_id=bros_bro_id,
                body="%s changed the description" % chat2.get_bros_bro_name_or_alias(),
                text_message="",
                timestamp=datetime.utcnow(),
                info=True
            )
            db.session.add(bro_message)
            db.session.commit()
            room = get_a_room_you_two(logged_in_bro.id, bros_bro_id)
            emit("message_event_send", bro_message.serialize, room=room)


def change_chat_alias(data):
    token = data["token"]
    bros_bro_id = data["bros_bro_id"]
    alias = data["alias"]
    logged_in_bro = Bro.verify_auth_token(token)
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
            room_bro = "room_%s" % logged_in_bro.id
            emit("message_event_chat_changed", chat1.serialize, room=room_bro)


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
            room_bro_1 = "room_%s" % logged_in_bro.id
            room_bro_2 = "room_%s" % bros_bro_id
            emit("message_event_chat_changed", chat1.serialize, room=room_bro_1)
            emit("message_event_chat_changed", chat2.serialize, room=room_bro_2)

            # We create an info message with the person who did the update as sender
            bro_message = Message(
                sender_id=logged_in_bro.id,
                recipient_id=bros_bro_id,
                body="%s changed the chat colour" % chat2.get_bros_bro_name_or_alias(),
                text_message="",
                timestamp=datetime.utcnow(),
                info=True
            )
            db.session.add(bro_message)
            db.session.commit()
            room = get_a_room_you_two(logged_in_bro.id, bros_bro_id)
            emit("message_event_send", bro_message.serialize, room=room)


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
            update_broups(broup_objects)
            # We create an info message with the person who did the update as sender
            broup_message = BroupMessage(
                sender_id=logged_in_bro.id,
                broup_id=broup_id,
                body="%s changed the description" % logged_in_bro.get_full_name(),
                text_message="",
                timestamp=datetime.utcnow(),
                info=True
            )
            db.session.add(broup_message)
            db.session.commit()
            broup_room = "broup_%s" % broup_id
            emit("message_event_send", broup_message.serialize, room=broup_room)


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
            room_bro = "room_%s" % logged_in_bro.id
            emit("message_event_chat_changed", broup.serialize, room=room_bro)


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
            update_broups(broup_objects)
            # We create an info message with the person who did the update as sender
            broup_message = BroupMessage(
                sender_id=logged_in_bro.id,
                broup_id=broup_id,
                body="%s changed the chat colour" % logged_in_bro.get_full_name(),
                text_message="",
                timestamp=datetime.utcnow(),
                info=True
            )
            db.session.add(broup_message)
            db.session.commit()
            broup_room = "broup_%s" % broup_id
            emit("message_event_send", broup_message.serialize, room=broup_room)


def change_bromotion(data):
    token = data["token"]
    logged_in_bro = Bro.verify_auth_token(token)

    if logged_in_bro is None:
        emit("message_event_bromotion_change", "token authentication failed", room=request.sid)
    else:
        old_bromotion = logged_in_bro.get_bromotion()
        new_bromotion = data["bromotion"]
        if Bro.query.filter_by(bro_name=logged_in_bro.bro_name, bromotion=new_bromotion).first() is not None:
            emit("message_event_bromotion_change", "broName bromotion combination taken", room=request.sid)
        else:
            logged_in_bro.set_bromotion(new_bromotion)
            all_chats = BroBros.query.filter_by(bros_bro_id=logged_in_bro.id).all()
            # update bromotion in the normal chats
            for chat in all_chats:
                chat.chat_name = logged_in_bro.get_full_name()
                db.session.add(chat)
                bro_room = "room_%s" % chat.bro_id
                emit("message_event_chat_changed", chat.serialize, room=bro_room)

            # update bromotion in all the broups this bro is a part of.
            all_broups = Broup.query.filter_by(bro_id=logged_in_bro.id).all()
            for brup in all_broups:
                # We need to update all the broup objects of a single broup id
                broups = Broup.query.filter_by(broup_id=brup.broup_id).all()
                for broup in broups:
                    broup_name = remove_last_occur(broup.get_broup_name(), old_bromotion)
                    broup_name = broup_name + "" + new_bromotion
                    broup.set_broup_name(broup_name)
                    db.session.add(broup)

                    bro_room = "room_%s" % broup.bro_id
                    emit("message_event_chat_changed", broup.serialize, room=bro_room)

            db.session.add(logged_in_bro)
            db.session.commit()
            update_broups(all_broups)
            emit("message_event_bromotion_change", "bromotion change successful", room=request.sid)


def mute_broup(data):
    token = data["token"]
    broup_id = data["broup_id"]
    bro_id = data["bro_id"]
    mute_time = data["mute"]

    logged_in_bro = Bro.verify_auth_token(token)

    mute = True
    unmute_date = None
    if mute_time == -1:
        mute = False
    elif mute_time == 0:
        unmute_date = datetime.now().utcnow() + timedelta(hours=1)
    elif mute_time == 1:
        unmute_date = datetime.now().utcnow() + timedelta(hours=8)
    elif mute_time == 2:
        unmute_date = datetime.now().utcnow() + timedelta(days=7)

    if logged_in_bro is None:
        emit("message_event_change_broup_mute_failed", "token authentication failed", room=request.sid)
    else:
        broup_of_bro = Broup.query.filter_by(broup_id=broup_id, bro_id=bro_id).first()
        if broup_of_bro is None:
            emit("message_event_change_broup_mute_failed", "broup finding failed", room=request.sid)
        else:
            broup_of_bro.mute_broup(mute)
            if not mute:
                broup_of_bro.set_mute_timestamp(None)
            if unmute_date:
                broup_of_bro.set_mute_timestamp(unmute_date)
            db.session.add(broup_of_bro)
            db.session.commit()
            room_bro = "room_%s" % logged_in_bro.id
            emit("message_event_chat_changed", broup_of_bro.serialize, room=room_bro)


def mute_chat(data):
    token = data["token"]
    bro_id = data["bro_id"]
    bros_bro_id = data["bros_bro_id"]
    mute_time = data["mute"]

    logged_in_bro = Bro.verify_auth_token(token)

    mute = True
    unmute_date = None
    if mute_time == -1:
        mute = False
    elif mute_time == 0:
        unmute_date = datetime.now().utcnow() + timedelta(hours=1)
    elif mute_time == 1:
        unmute_date = datetime.now().utcnow() + timedelta(hours=8)
    elif mute_time == 2:
        unmute_date = datetime.now().utcnow() + timedelta(days=7)

    if logged_in_bro is None:
        emit("message_event_change_chat_mute_failed", "token authentication failed", room=request.sid)
    else:
        chat = BroBros.query.filter_by(bro_id=bro_id, bros_bro_id=bros_bro_id).first()
        if chat is None:
            emit("message_event_change_chat_mute_failed", "chat finding failed", room=request.sid)
        else:
            chat.mute_chat(mute)
            if not mute:
                chat.set_mute_timestamp(None)
            if unmute_date:
                chat.set_mute_timestamp(unmute_date)
            db.session.add(chat)
            db.session.commit()
            room_bro = "room_%s" % logged_in_bro.id
            emit("message_event_chat_changed", chat.serialize, room=room_bro)

