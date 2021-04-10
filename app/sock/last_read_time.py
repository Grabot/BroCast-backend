from datetime import datetime

from app import db
from app.models.bro_bros import BroBros


def update_last_read_time(bro_id, bros_bro_id):
    print("going to update last read time!")
    bro_associate = BroBros.query.filter_by(bro_id=bro_id, bros_bro_id=bros_bro_id).first()

    # We assume this won't happen
    if bro_associate is None:
        return None

    print("set last read time")
    bro_associate.last_message_read_time_bro = datetime.utcnow
    print(bro_associate.last_message_read_time_bro)
    db.session.add(bro_associate)
    db.session.commit()


def get_last_read_time_bro(bro_id, bros_bro_id):
    print("going to read last read time!")
    # Note that the id's are flipped, since we want the read time of the other bro
    bro_associate = BroBros.query.filter_by(bro_id=bros_bro_id, bros_bro_id=bro_id).first()

    # We assume this won't happen
    if bro_associate is None:
        return None

    print(bro_associate.last_message_read_time_bro)
    return bro_associate.last_message_read_time_bro

