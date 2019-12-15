# Send to single device.
from pyfcm import FCMNotification
import config

push_service = FCMNotification(api_key=config.Config.API_Key)

registration_id = "ekhPxU_7Zbc:APA91bH-GC_b1vxPaJvsaHrO5bNa_6cpH46s24RtD6XOced8_au2rrgpX4j-EYcBAbGe0_ueDgBxFn0O5zpm3G2YO4JKIbZuEEVI9-fK0vJJNQIbTEM4M1of8B2yoJiSu0WrlA8gRYXs"
message_title = "BroCast Title"
message_body = "This is a message that hopefully is shown as a push notification on my emulator"
result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)

print(result)