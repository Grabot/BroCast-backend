from flask import request
from flask_socketio import emit
from app import db
from app.models.bro import Bro
from json import loads
from sqlalchemy import func
import random

from app.models.broup import Broup


def add_bro(data):
    token = data["token"]
    bros_bro_id = data["bros_bro_id"]
    logged_in_bro = Bro.verify_auth_token(token)
    if logged_in_bro:
        bro_to_be_added = Bro.query.filter_by(id=bros_bro_id).first()
        if bro_to_be_added:
            if bro_to_be_added.id != logged_in_bro.id:
                logged_in_bro.add_bro(bro_to_be_added)
                bro_to_be_added.add_bro(logged_in_bro)
                db.session.commit()
                bro_room = "room_%s" % bro_to_be_added.id
                emit("message_event_add_bro_success", "bro was added!", room=request.sid)
                emit("message_event_bro_added_you", "a bro has added you!", room=bro_room)
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
            bro.add_broup(broup_name, broup_id, bro_ids, broup_colour, admins)

        db.session.commit()
        emit("message_event_add_broup_success", "broup was added!", room=request.sid)
        # TODO: @Skools send broup creation update to all participants.
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

            db.session.commit()

            chat = Broup.query.filter_by(broup_id=broup_id, bro_id=logged_in_bro.id).first()
            if not chat:
                emit("message_event_add_bro_to_broup_failed", "adding bro to broup failed", room=request.sid)
            else:
                emit("message_event_add_bro_to_broup_success",
                     {
                         "result": True,
                         "chat": chat.serialize
                     }, room=request.sid)

