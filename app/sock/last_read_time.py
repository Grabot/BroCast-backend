from datetime import datetime
from datetime import timedelta
from flask import request
from flask_socketio import emit

from app import db
from app.models.bro_bros import BroBros
from app.models.broup import Broup
from app.models.broup_message import BroupMessage
from app.models.message import Message


def update_read_time(bro_id, bros_bro_id, room):
    read_time = update_last_read_time(bro_id, bros_bro_id)
    if read_time is not None:
        emit("message_event_read", read_time.strftime('%Y-%m-%dT%H:%M:%S.%f'), room=room)


def update_last_read_time(bro_id, bros_bro_id):
    bro_me = BroBros.query.filter_by(bro_id=bro_id, bros_bro_id=bros_bro_id).first()
    bro_other = BroBros.query.filter_by(bro_id=bros_bro_id, bros_bro_id=bro_id).first()

    # We assume this won't happen
    if bro_me is None or bro_other is None:
        return None

    bro_me.update_last_message_read_time_bro()
    bro_me.read_messages()
    read_time_other_bro = bro_other.get_last_message_read_time_bro()

    # We have just read the message so the read time of the other bro is the lowest.
    # All of the messages below that read time are also read by them, so we can remove them from the server
    # They should be stored on both of the phones locally so they can always read them again if they want
    messages = Message.query.filter_by(sender_id=bro_id, recipient_id=bros_bro_id) \
        .union(Message.query.filter_by(sender_id=bros_bro_id, recipient_id=bro_id)) \
        .filter(Message.timestamp < (read_time_other_bro - timedelta(minutes=5))) \
        .all()
    for message in messages:
        db.session.delete(message)

    db.session.add(bro_me)
    db.session.commit()
    # We have just update our own read time.
    # We will send the read time back of the other bro since it will be used to determine if both bros have read it
    return read_time_other_bro


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
            if not broup.has_left() and not broup.is_removed():
                if broup.get_last_message_read_time_bro() < lowest_read_time:
                    lowest_read_time = broup.get_last_message_read_time_bro()
    return lowest_read_time


def update_read_time_broup(bro_id, broup_id, broup_room):
    broup_of_bro = Broup.query.filter_by(broup_id=broup_id, bro_id=bro_id).first()
    # We assume this won't happen
    if broup_of_bro is None:
        return None

    read_time = datetime.utcnow()
    broup_of_bro.update_last_message_read_time_bro()
    broup_of_bro.read_messages()

    lowest_read_time = get_lowest_read_time_broup(broup_id, read_time)

    # We have just read the message so the read time of the other bro is the lowest.
    # All of the messages below that read time are also read by them, so we can remove them from the server
    # They should be stored on both of the phones locally so they can always read them again if they want
    messages = BroupMessage.query \
        .filter_by(broup_id=broup_id) \
        .filter(BroupMessage.timestamp < (lowest_read_time - timedelta(minutes=5))) \
        .order_by(BroupMessage.timestamp.desc()) \
        .all()
    for message in messages:
        db.session.delete(message)

    db.session.add(broup_of_bro)
    db.session.commit()

    if lowest_read_time is not None:
        emit("message_event_read", lowest_read_time.strftime('%Y-%m-%dT%H:%M:%S.%f'), room=broup_room)
