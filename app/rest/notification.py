from pyfcm import FCMNotification
from config import Config

push_service = FCMNotification(api_key="AAAA8jx_OQM:APA91bHyg05-yjvRv0yhD9o1bVyiniAsZsak7JUZlLLMu7U2iPoDJubrDHYI-29c373NAWEzoWiBEJQCWvQ1Pw246XkjBZbMgDw0zn1mndYbyZ4NkVmzccrFJYPbx4A-KOt85rtR_kBj")


def send_notification(bro, title, body):
    # send_result = push_service.notify_single_device(registration_id, message_title=title, message_body=body)
    send_result = push_service.notify_single_device(
        registration_id=bro.get_registration_id(),
        tag="message",
        title_loc_key="notification_message",
        message_title=title,
        message_body=body,
        sound="brodio"
    )
    print(send_result)

