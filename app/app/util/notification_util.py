from firebase_admin import messaging, credentials
import firebase_admin
from app.config.config import settings

cred_dict = {
    "type": "service_account",
    "project_id": settings.FIREBASE_PROJECT_ID,
    "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
    "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
    "client_email": settings.FIREBASE_CLIENT_EMAIL,
    "client_id": settings.FIREBASE_CLIENT_ID,
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": settings.FIREBASE_CLIENT_X509_CERT_URL,
    "universe_domain": "googleapis.com",
}

cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

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
                    channel_id="channel_bro",
                    click_action="FLUTTER_NOTIFICATION_CLICK"
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
                        ),
                        sound="res_brodio.caf"
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

