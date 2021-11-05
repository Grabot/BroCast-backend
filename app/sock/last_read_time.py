from datetime import datetime

from flask import request
from flask_socketio import emit

from app import db
from app.models.bro_bros import BroBros
from app.models.broup import Broup


def update_read_time(bro_id, bros_bro_id, room):
    read_time = update_last_read_time(bro_id, bros_bro_id)
    if read_time is not None:
        emit("message_event_read", read_time.strftime('%Y-%m-%dT%H:%M:%S.%f'), room=room)


def update_last_read_time(bro_id, bros_bro_id):
    bro_associate = BroBros.query.filter_by(bro_id=bro_id, bros_bro_id=bros_bro_id).first()

    # We assume this won't happen
    if bro_associate is None:
        return None

    read_time = datetime.utcnow()
    bro_associate.last_message_read_time_bro = read_time
    bro_associate.read_messages()
    db.session.add(bro_associate)
    db.session.commit()
    return read_time


def get_last_read_time_other_bro(bro_id, bros_bro_id):
    # Note that the id's are flipped, since we want the read time of the other bro
    bro_associate = BroBros.query.filter_by(bro_id=bros_bro_id, bros_bro_id=bro_id).first()

    # We assume this won't happen
    if bro_associate is None:
        return None

    return bro_associate.last_message_read_time_bro


def get_lowest_read_time_broup(broup_id, read_time):
    lowest_read_time = read_time
    broup_objects = Broup.query.filter_by(broup_id=broup_id)
    if broup_objects is None:
        emit("message_event_read_failed", "updating messages failed", room=request.sid)
    else:
        for broup in broup_objects:
            if broup.get_last_message_read_time_bro() < lowest_read_time:
                lowest_read_time = broup.get_last_message_read_time_bro()
    return lowest_read_time


def update_read_time_broup(bro_id, broup_id, broup_room):
    broup_of_bro = Broup.query.filter_by(broup_id=broup_id, bro_id=bro_id).first()
    # We assume this won't happen
    if broup_of_bro is None:
        return None

    read_time = datetime.utcnow()
    broup_of_bro.update_last_message_read_time_bro(read_time)
    broup_of_bro.read_messages()
    db.session.add(broup_of_bro)
    db.session.commit()

    lowest_read_time = get_lowest_read_time_broup(broup_id, read_time)

    if lowest_read_time is not None:
        emit("message_event_read", lowest_read_time.strftime('%Y-%m-%dT%H:%M:%S.%f'), room=broup_room)
