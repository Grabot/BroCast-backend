from flask import request
from flask_socketio import emit
from app import db
from app.models.bro import Bro
from json import loads
from sqlalchemy import func
import random

from app.models.broup import Broup
from app.models.broup_message import BroupMessage


def add_bro(data):
    token = data["token"]
    bros_bro_id = data["bros_bro_id"]
    logged_in_bro = Bro.verify_auth_token(token)
    if logged_in_bro:
        bro_to_be_added = Bro.query.filter_by(id=bros_bro_id).first()
        if bro_to_be_added:
            if bro_to_be_added.id != logged_in_bro.id:
                chat_colour = '%02X%02X%02X' % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                bros_bro = logged_in_bro.add_bro(bro_to_be_added, chat_colour)
                bros_bro_added_bro = bro_to_be_added.add_bro(logged_in_bro, chat_colour)
                db.session.commit()
                bro_room = "room_%s" % bro_to_be_added.id
                if bros_bro:
                    emit("message_event_add_bro_success", bros_bro.serialize, room=request.sid)
                else:
                    emit("message_event_add_bro_failed", "Bro was already added", room=request.sid)

                if bros_bro_added_bro:
                    emit("message_event_bro_added_you", bros_bro_added_bro.serialize, room=bro_room)
            else:
                emit("message_event_add_bro_failed", "You tried to add yourself", room=request.sid)
        else:
            emit("message_event_add_bro_failed", "failed to add bro", room=request.sid)
    else:
        emit("message_event_add_bro_failed", "failed to add bro", room=request.sid)


def add_broup(data):
    token = data["token"]
    logged_in_bro = Bro.verify_auth_token(token)
    if not logged_in_bro:
        emit("message_event_add_broup_failed", "failed to add broup", room=request.sid)
    else:
        participants = loads(data["participants"])

        broup_name = data["broup_name"]
        broup_name += " " + logged_in_bro.bromotion

        max_broup_id = db.session.query(func.max(Broup.broup_id)).scalar()
        if max_broup_id is None:
            max_broup_id = 0
        broup_id = max_broup_id + 1

        bro_ids = [logged_in_bro.id]
        admins = [logged_in_bro.id]
        broup = [logged_in_bro]
        for part in participants:
            bro_for_broup = Bro.query.filter_by(id=part).first()
            if bro_for_broup is None:
                emit("message_event_add_broup_failed", "failed to add broup", room=request.sid)
                return
            else:
                broup.append(bro_for_broup)
                broup_name += "" + bro_for_broup.bromotion
                bro_ids.append(bro_for_broup.id)

        broup_colour = '%02X%02X%02X' % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        for bro in broup:
            b = bro.add_broup(broup_name, broup_id, bro_ids, broup_colour, admins)
            room = "room_%s" % bro.id
            if b is not None:
                emit("message_event_added_to_broup", b.serialize, room=room)

        db.session.commit()

        emit("message_event_add_broup_success", "broup was added!", room=request.sid)
        return


def add_bro_to_broup(data):
    token = data["token"]
    logged_in_bro = Bro.verify_auth_token(token)
    if not logged_in_bro:
        emit("message_event_add_bro_to_broup_failed", "adding bro to broup failed", room=request.sid)
    else:
        broup_id = data["broup_id"]
        bro_id = data["bro_id"]

        broup_objects = Broup.query.filter_by(broup_id=broup_id)
        if broup_objects is None:
            emit("message_event_add_bro_to_broup_failed", "adding bro to broup failed", room=request.sid)
            return
        else:
            new_bro_for_broup = Bro.query.filter_by(id=bro_id).first()
            if not new_bro_for_broup:
                emit("message_event_add_bro_to_broup_failed", "adding bro to broup failed", room=request.sid)
                return
            broup_name = ""
            broup_colour = ""
            broup_description = ""
            bro_ids = [bro_id]
            admins = []
            for broup in broup_objects:
                broup_name = broup.get_broup_name() + "" + new_bro_for_broup.get_bromotion()
                broup.set_broup_name(broup_name)
                broup.add_participant(bro_id)
                db.session.add(broup)
                # Appending the bro ids from each of the broups
                bro_ids.append(broup.get_bro_id())
                # These should be the same in all broup objects
                admins = broup.get_admins()
                broup_colour = broup.get_broup_colour()
                broup_description = broup.get_broup_description()

            new_bro_for_broup.add_broup(broup_name, broup_id, bro_ids, broup_colour, admins, broup_description)
            new_bro_room = "room_%s" % new_bro_for_broup.id
            emit("message_event_added_to_broup", "you got added to a broup!", room=new_bro_room)

            db.session.commit()

            broup_room = "broup_%s" % broup_id
            emit("message_event_broup_changed", "there was an update to a broup!", room=broup_room)

            chat = Broup.query.filter_by(broup_id=broup_id, bro_id=logged_in_bro.id).first()
            if not chat:
                emit("message_event_add_bro_to_broup_failed", "adding bro to broup failed", room=request.sid)
            else:
                emit("message_event_add_bro_to_broup_success",
                     {
                         "result": True,
                         "chat": chat.serialize
                     }, room=request.sid)


def remove_last_occur(old_string, bromotion):
    new_string = ''
    length = len(old_string)

    for i in range(length-1, 0, -1):
        if old_string[i] == bromotion:
            new_string = old_string[0:i] + old_string[i + 1:length]
            break
    return new_string


def change_broup_remove_bro(data):
    token = data["token"]
    broup_id = data["broup_id"]
    bro_id = data["bro_id"]
    logged_in_bro = Bro.verify_auth_token(token)

    if logged_in_bro is None:
        emit("message_event_change_broup_remove_bro_failed", "token authentication failed", room=request.sid)
    else:
        broup_objects = Broup.query.filter_by(broup_id=broup_id)
        remove_broup = Broup.query.filter_by(broup_id=broup_id, bro_id=bro_id).first()
        remove_bro = Bro.query.filter_by(id=bro_id).first()
        if broup_objects is None or remove_broup is None or remove_bro is None:
            emit("message_event_change_broup_remove_bro_failed", "broup finding failed", room=request.sid)
        else:
            remove_bromotion = remove_bro.get_bromotion()
            for broup in broup_objects:
                broup_name = remove_last_occur(broup.get_broup_name(), remove_bromotion)
                broup.set_broup_name(broup_name)
                broup.remove_bro(bro_id)
                db.session.add(broup)

            # It's possible, that the user left the broup and that there are no more bros left.
            # In this case we will remove all the messages
            if len(remove_broup.get_participants()) == 0:
                messages = BroupMessage.query.filter_by(broup_id=broup_id)
                for message in messages:
                    db.session.delete(message)
                remove_broup.broup_removed()
                db.session.add(remove_broup)
            else:
                # We'll only remove the whole row if there are still bro's left in the broup
                # If it was the last bro, we leave an empty broup shell in the database for functional reasons
                db.session.delete(remove_broup)
            db.session.commit()

            broup_room = "broup_%s" % broup_id
            emit("message_event_broup_changed", "there was an update to a broup!", room=broup_room)

            emit("message_event_change_broup_remove_bro_success",
                 {
                     "result": True,
                     "old_bro": bro_id
                 },
                 room=request.sid)

