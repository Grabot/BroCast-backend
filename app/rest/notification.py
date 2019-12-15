# Send to single device.
from pyfcm import FCMNotification
from config import Config

registration_id = "fX9f-AHpl7c:APA91bHd9HO6T00QSMxTmKi5yy4klDMsP1k075_tSvStMG9XmjdTJ0mYeFe2JQoxB9y7F1PwUVr5jxkMbbGdOg99ZGAU-oxW8l4JLyeN8A9Ks8VKXhvBjpbyZe7M7WJdLCHb54xM9Doa"

push_service = FCMNotification(api_key=Config.API_Key)

def send_notification(bro, title, body):
    print("send notification")
    print("api: " + Config.API_Key)
    print("registration: " + registration_id)
    send_result = push_service.notify_single_device(registration_id, message_title=title, message_body=body)
    # send_result = push_service.notify_single_device(registration_id=bro.registration_id, message_title=title, message_body=body)
    print(send_result)

