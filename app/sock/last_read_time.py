from datetime import datetime
from flask_socketio import emit

from app import db
from app.models.bro_bros import BroBros


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


def update_read_time_broup(bro_id, broup_id, broup_room):
    # TODO: @SKools implementatie
    print("updating broup read time")
