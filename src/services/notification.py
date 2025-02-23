from typing import Iterable

from src.base import SingletonMeta
from src.logger import logger
from src.types import FirebaseMessageItem, SesEmailItem

from .firebase import FirebaseMessagingService
from .ses import SesService


class NotificationService(metaclass=SingletonMeta):
    def __init__(self):
        self.firebase_messaging_service = FirebaseMessagingService()
        self.ses_service = SesService()

    def send_ses_emails(self, emails: Iterable[SesEmailItem]):
        for email in emails:
            try:
                self.ses_service.send_emails(email)
            except Exception as e:
                logger.error(f"Failed to send {email}: {e}")

    def send_firebase_messages(self, messages: Iterable[FirebaseMessageItem]):
        for message in messages:
            if message.registration_tokens:
                try:
                    self.firebase_messaging_service.send_messages(message)
                except Exception as e:
                    logger.error(f"Failed to send {message}: {e}")
