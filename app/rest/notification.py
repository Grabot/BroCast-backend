from app.config import Config
from app.models.bro import Bro
from pyfcm import FCMNotification
from pyfcm.errors import AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError


push_service = FCMNotification(api_key=Config.NOTIFICATION_KEY)


def send_notification(data):

    bro_id = data["bro_id"]
    bros_bro_id = data["bros_bro_id"]

    bro_to_notify = Bro.query.filter_by(id=bros_bro_id).first()
    if bro_to_notify is None or bro_to_notify.get_registration_id() == "":
        return ""

    bro_who_send = Bro.query.filter_by(id=bro_id).first()
    if bro_who_send is None:
        return ""

    message_body = data["message"]
    message_title = "message from %s %s" % (bro_who_send.bro_name, bro_who_send.bromotion)

    data_message = {
        "id": bro_who_send.id,
        "bro_name": bro_who_send.bro_name,
        "bromotion": bro_who_send.bromotion
    }

    registration_id = bro_to_notify.get_registration_id()
    result = ""
    try:
        result = push_service.notify_single_device(
            registration_id=registration_id,
            message_title=message_title,
            message_body=message_body,
            data_message=data_message,
            sound="brodio"
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
    print(result)


