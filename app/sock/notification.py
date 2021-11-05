from datetime import datetime
from app.config import Config
from app.models.bro import Bro
from app.models.bro_bros import BroBros
from pyfcm import FCMNotification
from pyfcm.errors import AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError
from app import db

push_service = FCMNotification(api_key=Config.NOTIFICATION_KEY)


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

    message_body = data["message"]

    chat = bro_bros.serialize

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

    device_type_bro_to_notify = bro_to_notify.get_device_type()
    try:
        if device_type_bro_to_notify == "Android":
            data_message = {
                "id": chat["bros_bro_id"],
                "chat_name": chat["chat_name"],
                "alias": chat["alias"],
                "broup": False,
                "message_body": message_body
            }

            push_service.single_device_data_message(
                registration_id=registration_id,
                data_message=data_message
            )
        else:
            chat_name = chat["chat_name"]
            if chat["alias"] is not None and chat["alias"] != "":
                chat_name = chat["alias"]
            push_service.notify_single_device(
                registration_id=registration_id,
                message_title=chat_name,
                message_body=message_body
            )
    except AuthenticationError:
        print("There was a big issue with the firebase key. Fix it, quick!")
    except FCMServerError:
        print("Something was wrong with the firebase server. Let's hope they fix it fast")
    except InvalidDataError:
        print("The message was not formatted correctly! Find out what happened!")
    except InternalPackageError:
        print("there was an error or something. Not in the package, but the package within the package? internally? "
              "Let's hope this never happens")


def send_notification_broup(bro_ids, message_body, broup_id, broup_objects, me_id):
    bro_registration_ids_android = []
    bro_registration_ids_other = []
    # It might happen that we only have 1 bro to send it too,
    # in this case we have extra information we can send with the notification to make it easier
    broup_android = None
    for bro_id in bro_ids:
        bro_to_notify = Bro.query.filter_by(id=bro_id).first()
        broup = [br for br in broup_objects if br.bro_id == bro_id]
        if bro_to_notify is not None \
                and broup is not None and broup[0] is not None \
                and bro_to_notify.id != me_id \
                and bro_to_notify.get_registration_id() != "" \
                and bro_to_notify.get_device_type() != "":
            if broup[0].check_mute():
                db.session.add(broup[0])
                db.session.commit()
            if not broup[0].is_muted():
                if bro_to_notify.get_device_type() == "Android":
                    bro_registration_ids_android.append(bro_to_notify.get_registration_id())
                    broup_android = broup[0]
                else:
                    bro_registration_ids_other.append([bro_to_notify.get_registration_id(), broup[0]])

    try:
        if len(bro_registration_ids_android) >= 2:
            data_message = {
                "id": broup_id,
                "broup": True,
                "message_body": message_body
            }

            push_service.notify_multiple_devices(
                registration_ids=bro_registration_ids_android,
                data_message=data_message
            )
        elif len(bro_registration_ids_android) == 1:
            data_message = {
                "id": broup_id,
                "broup": True,
                "message_body": message_body
            }
            if broup_android is not None:
                data_message = {
                    "id": broup_id,
                    "chat_name": broup_android.get_broup_name(),
                    "alias": broup_android.get_alias(),
                    "broup": True,
                    "message_body": message_body
                }
            push_service.single_device_data_message(
                registration_id=bro_registration_ids_android[0],
                data_message=data_message
            )
        if len(bro_registration_ids_other) >= 2:
            for other_phone in bro_registration_ids_other:
                title = other_phone[1].get_broup_name()
                alias = other_phone[1].get_alias()
                if alias != "":
                    title = alias
                push_service.notify_single_device(
                    registration_id=other_phone[0],
                    message_title=title,
                    message_body=message_body
                )
        elif len(bro_registration_ids_other) == 1:
            title = bro_registration_ids_other[0][1].get_broup_name()
            alias = bro_registration_ids_other[0][1].get_alias()
            if alias != "":
                title = alias
            push_service.notify_single_device(
                registration_id=bro_registration_ids_other[0][0],
                message_title=title,
                message_body=message_body
            )
    except AuthenticationError:
        print("There was a big issue with the firebase key. Fix it, quick!")
    except FCMServerError:
        print("Something was wrong with the firebase server. Let's hope they fix it fast")
    except InvalidDataError:
        print("The message was not formatted correctly! Find out what happened!")
    except InternalPackageError:
        print("there was an error or something. Not in the package, but the package within the package? internally? "
              "Let's hope this never happens")
