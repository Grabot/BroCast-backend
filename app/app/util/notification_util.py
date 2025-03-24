from firebase_admin import messaging, credentials
import firebase_admin


cred = credentials.Certificate("brocast_firebase.json")
test = firebase_admin.initialize_app(cred)

async def send_notification_broup(tokens, broup_id, private, broup_name, sender_name, message):
    message_title = f"New message in {broup_name}"
    message_body = message
    if private:
        message_title = f"New message from {sender_name}"
    for token_detail in tokens:
        token = token_detail[0]
        platform = token_detail[1]
        notification = messaging.Notification(
            title=message_title,
            body=message_body,
        )
        message_data = {
            "broup_id": str(broup_id),
        }
        
        # Platform-specific configuration
        if platform == 0:
            android_config = messaging.AndroidConfig(
                notification=messaging.AndroidNotification(
                    channel_id="channel_bro"
                )
            )
            message = messaging.Message(
                notification=notification,
                data=message_data,
                android=android_config,
                token=token
            )
        elif platform == 1:
            # TODO: test
            apns_config = messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        alert=messaging.ApsAlert(
                            title=message_title,
                            body=message_body,
                        )
                    )
                )
            )
            message = messaging.Message(
                notification=notification,
                data=message_data,
                apns=apns_config,
                token=token
            )
        else:
            raise ValueError("Unsupported platform")
        
        # Send the message
        try:
            _ = messaging.send(message)
        except Exception as e:
            print(f"Error sending message: {e}")

