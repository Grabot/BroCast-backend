from pyfcm import FCMNotification
from config import Config

push_service = FCMNotification(api_key=Config.API_Key)


def send_notification(bro, title, body):
    # send_result = push_service.notify_single_device(registration_id, message_title=title, message_body=body)
    send_result = push_service.notify_single_device(
        registration_id=bro.get_registration_id(),
        message_title=title,
        message_body=body
    )
    print(send_result)

