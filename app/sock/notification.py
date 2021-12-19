import requests
from app.config import Config
from app.models.bro import Bro
from app.models.bro_bros import BroBros
from app import db


def send_notification(data):
    bro_id = data["bro_id"]
    bros_bro_id = data["bros_bro_id"]

    bro_to_notify = Bro.query.filter_by(id=bros_bro_id).first()
    if bro_to_notify is None or bro_to_notify.get_registration_id() == "":
        return ""

    # We need the chat object of the bro we're notifying
    bro_bros = BroBros.query.filter_by(bro_id=bros_bro_id, bros_bro_id=bro_id).first()
    if bro_bros is None:
        return ""

    registration_id = None
    if not bro_bros.is_muted():
        registration_id = bro_to_notify.get_registration_id()
    else:
        if bro_bros.check_mute():
            db.session.add(bro_bros)
            db.session.commit()
        if not bro_bros.is_muted():
            registration_id = bro_to_notify.get_registration_id()

    if registration_id is None:
        # If the registration id is not set the chat was muted.
        return

    message_body = data["message"]
    message_title = bro_bros.alias
    if message_title is None or message_title == "":
        message_title = bro_bros.chat_name

    notify(message_body, message_title, registration_id, bro_id, 0)


def send_notification_broup(bro_ids, message_body, broup_id, broup_objects, me_id):
    for bro_id in bro_ids:
        bro_to_notify = Bro.query.filter_by(id=bro_id).first()
        broup = [br for br in broup_objects if br.bro_id == bro_id]
        if bro_to_notify is not None \
                and broup is not None and broup[0] is not None \
                and bro_to_notify.id != me_id \
                and bro_to_notify.get_registration_id() != "":
            if broup[0].check_mute():
                db.session.add(broup[0])
                db.session.commit()
            if not broup[0].is_muted() or not broup[0].has_left() or not broup[0].is_removed():
                message_title = broup[0].alias
                if message_title is None or message_title == "":
                    message_title = broup[0].broup_name
                notify(message_body, message_title, bro_to_notify.get_registration_id(), broup_id, 1)


def notify(message_body, message_title, registration_id, chat_id, broup):

    server_token = Config.NOTIFICATION_KEY
    headers = {
        'Content-type': 'application/json',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Authorization': 'key=' + server_token
    }
    r = requests.post(Config.FIREBASE_URL, json={
        'to': registration_id,
        'notification': {
            'body': message_body,
            'title': message_title,
            'android_channel_id': 'custom_sound',
            'sound': 'res_brodio.aiff',
            'icon': 'res_bro_icon'
        },
        'data': {
            'id': chat_id,
            'broup': broup
        }
    }, headers=headers)

    if r.status_code != 200:
        print("Not possible to send notifications at this time")
