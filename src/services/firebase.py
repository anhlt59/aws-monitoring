import json

import firebase_admin
from firebase_admin import credentials, messaging

from src.constants import FIREBASE_CREDENTIALS, FIREBASE_TIME_OUT
from src.logger import logger
from src.types import FirebaseMessageItem

firebase_credential = credentials.Certificate(json.loads(FIREBASE_CREDENTIALS))
firebase_admin.initialize_app(firebase_credential, {"httpTimeout": FIREBASE_TIME_OUT})


class FirebaseMessagingService:
    def send_messages(self, message: FirebaseMessageItem):
        if not message.registration_tokens:
            logger.error("Failed to send Firebase message, registration_tokens is required")
            return None

        # Create a message to send
        multicast_message = messaging.MulticastMessage(
            notification=messaging.Notification(title=message.title, body=message.body),
            data=message.data,
            tokens=message.registration_tokens,
            android=messaging.AndroidConfig(priority="normal", data={"content_available": "false"}),
            apns=messaging.APNSConfig(
                headers={"apns-priority": "5"},
                payload=messaging.APNSPayload(aps=messaging.Aps(content_available=False, badge=message.badge)),
            ),
        )
        # Send the message
        response = messaging.send_each_for_multicast(multicast_message)

        success = []
        failure = []
        for idx, resp in enumerate(response.responses):
            if not resp.success:
                failure.append(f"Token<{message.registration_tokens[idx]:.20}> failed: {resp.exception}")
            else:
                success.append(f"Token<{message.registration_tokens[idx]:.20}")

        if success:
            logger.info(f"Sent {len(success)} Message<id={message.id}> successfully: {success}")
        if failure:
            logger.warning(f"Failed to sent {len(failure)} Message<id={message.id}>: {failure}")
