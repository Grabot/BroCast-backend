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
        # chat was muted, but maybe it can be unmuted
        if bro_bros.get_mute_timestamp() and bro_bros.get_mute_timestamp() < datetime.now().utcnow():
            print("the bro had it muted temporarily and the time has run out!")
            bro_bros.set_mute_timestamp(None)
            bro_bros.mute_chat(False)
            db.session.add(bro_bros)
            db.session.commit()

            registration_id = bro_to_notify.get_registration_id()

    if registration_id is None:
        # If the registration id is not set the chat was muted.
        return

    device_type_bro_to_notify = bro_to_notify.get_device_type()
    try:
        if device_type_bro_to_notify == "Android":
            data_message = {
                "chat": chat,
                "message_body": message_body
            }

            push_service.single_device_data_message(
                registration_id=registration_id,
                data_message=data_message
            )
        else:
            push_service.notify_single_device(
                registration_id=registration_id,
                message_title=chat["chat_name"],
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


def send_notification_broup(bro_ids, message_body, chat, broup_objects, me_id):
    print("sending notifications to a whole broup")
    bro_registration_ids_android = []
    bro_registration_ids_other = []
    for bro_id in bro_ids:
        bro_to_notify = Bro.query.filter_by(id=bro_id).first()
        broup = [br for br in broup_objects if br.bro_id == bro_id]
        if bro_to_notify is not None \
                and broup is not None and broup[0] is not None \
                and bro_to_notify.id != me_id \
                and bro_to_notify.get_registration_id() != "" \
                and bro_to_notify.get_device_type() != "":
            if not broup[0].is_muted():
                if bro_to_notify.get_device_type() == "Android":
                    bro_registration_ids_android.append(bro_to_notify.get_registration_id())
                else:
                    bro_registration_ids_other.append(bro_to_notify.get_registration_id())
            else:
                # broup was muted, but maybe it can be unmuted
                if broup[0].get_mute_timestamp() and broup[0].get_mute_timestamp() < datetime.now().utcnow():
                    print("the bro had it muted temporarily and the time has run out!")
                    broup[0].set_mute_timestamp(None)
                    broup[0].mute_broup(False)
                    db.session.add(broup[0])

                    if bro_to_notify.get_device_type() == "Android":
                        bro_registration_ids_android.append(bro_to_notify.get_registration_id())
                    else:
                        bro_registration_ids_other.append(bro_to_notify.get_registration_id())

    db.session.commit()
    try:
        if len(bro_registration_ids_android) >= 2:
            print("sending to multiple androids")
            print(bro_registration_ids_android)
            data_message = {
                "chat": chat,
                "message_body": message_body
            }

            push_service.notify_multiple_devices(
                registration_ids=bro_registration_ids_android,
                data_message=data_message
            )
        elif len(bro_registration_ids_android) == 1:
            print("sending to single androids")
            print(bro_registration_ids_android)
            data_message = {
                "chat": chat,
                "message_body": message_body
            }

            push_service.single_device_data_message(
                registration_id=bro_registration_ids_android[0],
                data_message=data_message
            )
        if len(bro_registration_ids_other) >= 2:
            print("sending to multiple others")
            print(bro_registration_ids_other)
            push_service.notify_multiple_devices(
                registration_ids=bro_registration_ids_other,
                message_title=chat["chat_name"],
                message_body=message_body
            )
        elif len(bro_registration_ids_other) == 1:
            print("sending to single other")
            push_service.notify_single_device(
                registration_id=bro_registration_ids_other[0],
                message_title=chat["chat_name"],
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
