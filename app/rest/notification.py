from app.config import Config
from app.models.bro import Bro
from app.models.bro_bros import BroBros
from pyfcm import FCMNotification
from pyfcm.errors import AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError


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

    registration_id = bro_to_notify.get_registration_id()
    device_type_bro_to_notify = bro_to_notify.get_device_type()
    try:
        if device_type_bro_to_notify == "Android":

            data_message = {
                "chat": bro_bros.serialize,
                "message_body": message_body
            }

            push_service.single_device_data_message(
                registration_id=registration_id,
                data_message=data_message
            )
        else:
            friend_name = bro_to_notify.bro_name + " " + bro_to_notify.bromotion
            push_service.notify_single_device(
                registration_id=registration_id,
                message_title=friend_name,
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


