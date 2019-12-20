from pyfcm import FCMNotification
from config import Config

push_service = FCMNotification(api_key=Config.API_Key)


def send_notification(bro, title, body):
    # send_result = push_service.notify_single_device(registration_id, message_title=title, message_body=body)
    try:
        send_result = push_service.notify_single_device(
            registration_id=bro.get_registration_id(),
            tag="message",
            title_loc_key="notification_message",
            message_title=title,
            message_body=body,
            sound="brodio"
        )
        print(send_result)
    except:
        print("something went wrong, no notification send")


