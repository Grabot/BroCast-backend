from flask import request
from flask_socketio import emit
from app import db
from app.models.bro import Bro
from json import loads
from sqlalchemy import func
import random

from app.models.bro_bros import BroBros
from app.models.broup import Broup
from app.models.broup_message import BroupMessage
from datetime import datetime

from app.util.util import remove_last_occur, update_broups


def add_bro(data):
    token = data["token"]
    bros_bro_id = data["bros_bro_id"]
    logged_in_bro = Bro.verify_auth_token(token)
    if logged_in_bro:
        bro_to_be_added = Bro.query.filter_by(id=bros_bro_id).first()

        logged_in_bro_room = "room_%s" % logged_in_bro.id
        bro_added_exists = BroBros.query.filter_by(bro_id=logged_in_bro.id, bros_bro_id=bros_bro_id).first()
        if bro_added_exists:
            # If the bro object already exists, he is probably removed. We will undo the removing.
            bro_added_exists.re_join()
            db.session.add(bro_added_exists)
            db.session.commit()
            emit("message_event_add_bro_success", bro_added_exists.serialize, room=logged_in_bro_room)
        elif bro_to_be_added:
            if bro_to_be_added.id != logged_in_bro.id:
                chat_colour = '%02X%02X%02X' % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                bros_bro = logged_in_bro.add_bro(bro_to_be_added, chat_colour)
                bros_bro_added_bro = bro_to_be_added.add_bro(logged_in_bro, chat_colour)
                db.session.commit()
                if bros_bro:
                    emit("message_event_add_bro_success", bros_bro.serialize, room=logged_in_bro_room)
                else:
                    emit("message_event_add_bro_failed", "Bro was already added", room=logged_in_bro_room)

                if bros_bro_added_bro:
                    bro_room = "room_%s" % bro_to_be_added.id
                    emit("message_event_bro_added_you", bros_bro_added_bro.serialize, room=bro_room)
            else:
                emit("message_event_add_bro_failed", "You tried to add yourself", room=logged_in_bro_room)
        else:
            emit("message_event_add_bro_failed", "failed to add bro", room=logged_in_bro_room)
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

            bro_broup = Broup.query.filter_by(broup_id=broup_id, bro_id=bro_id).first()
            if bro_broup is not None and not bro_broup.has_left() and not bro_broup.is_removed():
                emit("message_event_add_bro_to_broup_failed", "adding bro to broup failed", room=request.sid)
            else:
                broup_name = ""
                broup_colour = ""
                broup_description = ""
                bro_ids = [bro_id]
                admins = []
                for broup in broup_objects:
                    if not broup.has_left() and not broup.is_removed():
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

                new_bro_room = "room_%s" % new_bro_for_broup.id
                if bro_broup:
                    # If a broup object already exists than it has to be because the bro left or removed this broup.
                    # We add the bro again to the broup
                    bro_broup.set_participants(bro_ids)
                    bro_broup.set_broup_name(broup_name)
                    bro_broup.set_admins(admins)
                    bro_broup.update_description(broup_description)
                    bro_broup.update_colour(broup_colour)
                    bro_broup.rejoin()
                    db.session.add(bro_broup)
                    emit("message_event_added_to_broup", bro_broup.serialize, room=new_bro_room)
                else:
                    b = new_bro_for_broup.add_broup(broup_name, broup_id, bro_ids, broup_colour, admins, broup_description)
                    if b is not None:
                        emit("message_event_added_to_broup", b.serialize, room=new_bro_room)

                broup_message = BroupMessage(
                    sender_id=bro_id,
                    broup_id=broup_id,
                    body="%s has been added to the broup!" % new_bro_for_broup.get_full_name(),
                    text_message="",
                    timestamp=datetime.utcnow(),
                    info=True
                )
                db.session.add(broup_message)
                db.session.commit()

                broup_room = "broup_%s" % broup_id
                emit("message_event_send", broup_message.serialize, room=broup_room)

                update_broups(broup_objects)


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

            # It's possible that the user who left was the only admin in the broup at the moment.
            # When there are no admins left we randomly assign a user to be admin.
            if len(remove_broup.get_admins()) == 0:
                # In this special event we will make everyone remaining an admin.
                for broup in broup_objects:
                    if not broup.has_left() and not broup.is_removed():
                        new_admin_id = broup.bro_id
                        for broup2 in broup_objects:
                            broup2.add_admin(new_admin_id)
                            db.session.add(broup2)

            # It's possible, that the user left the broup and that there are no more bros left.
            # In this case we will remove all the messages
            if len(remove_broup.get_participants()) == 0:
                messages = BroupMessage.query.filter_by(broup_id=broup_id)
                for message in messages:
                    db.session.delete(message)

            remove_broup.leave_broup()
            db.session.add(remove_broup)

            leave_message = "%s has been removed" % remove_bro.get_full_name()
            if bro_id == logged_in_bro.id:
                leave_message = "%s has left" % remove_bro.get_full_name()

            broup_message = BroupMessage(
                sender_id=bro_id,
                broup_id=broup_id,
                body=leave_message,
                text_message="",
                timestamp=datetime.utcnow(),
                info=True
            )
            db.session.add(broup_message)

            db.session.commit()

            update_broups(broup_objects)

            broup_room = "broup_%s" % broup_id
            emit("message_event_send", broup_message.serialize, room=broup_room)

            bro_room = "room_%s" % remove_broup.bro_id
            emit("message_event_chat_changed", remove_broup.serialize, room=bro_room)

