from collections import defaultdict
from datetime import timedelta
from typing import Any, Iterable

from sqlalchemy.orm import close_all_sessions

from src.constants import DATETIME_FORMAT
from src.logger import logger
from src.models import DeviceMonitorModel
from src.repositories import AccountRepository, DeviceMonitorRepository, NotifyUserRepository
from src.services.notification import NotificationService
from src.templates import ABNORMAL_EMAIL_TEMPLATE, EMAIL_TITLE_MAPPING, RECOVER_EMAIL_TEMPLATE
from src.types import EnableStatus, FirebaseMessageItem, MonitorStatus, SesEmailItem

JST_OFFSET = timedelta(hours=9)  # JST is UTC+9
account_repository = AccountRepository()
notification_service = NotificationService()
device_monitor_repository = DeviceMonitorRepository()
notify_user_repository = NotifyUserRepository()


def deserialize_sqs_record_to_device_monitor_models(record: Any) -> list[DeviceMonitorModel]:
    # logger.debug(f"Deserialize record: {record}")
    try:
        # parse JSON
        unverified_device_monitors = device_monitor_repository.deserialize_sqs_record(record)
        # if the device is not found, skip that record
        return device_monitor_repository.verify_device_monitors(list(unverified_device_monitors))
    except Exception as e:
        logger.error(f"Failed to deserialize record {record}: {e}")
        raise e


def load_notification_info(device_monitors: list[DeviceMonitorModel]) -> list[DeviceMonitorModel]:
    imeis = []
    account_ids = []
    device_monitor_ids = []
    for item in device_monitors:
        imeis.append(item.imei)
        account_ids.append(item.device.account_id)
        device_monitor_ids.append(item.id)

    # load account then mapping with device_monitors
    accounts = account_repository.list_accounts_with_notification_info(account_ids)
    account_mapping = {item.id: item for item in accounts}
    for device_monitor in device_monitors:
        if account := account_mapping.get(device_monitor.device.account_id):
            device_monitor.device.account = account

    # load notify_users then mapping with device_monitors
    notify_users = notify_user_repository.list_notify_users_by_account_id_and_imei(account_ids, imeis)
    notify_user_mapping = defaultdict(lambda: [])
    for imei, notify_user in notify_users:
        notify_user_mapping[imei].append(notify_user)
    for device_monitor in device_monitors:
        device_monitor.device.account.notify_users = notify_user_mapping[device_monitor.imei]
    return device_monitors


def create_firebase_item(device_monitor: DeviceMonitorModel) -> FirebaseMessageItem | None:
    account = device_monitor.device.account

    if device_monitor.push_firebase_message:
        registration_tokens = list(
            set(
                item.device_token
                for item in account.device_tokens
                if item.is_login == EnableStatus.ENABLE and item.device_token
            )
        )
        if registration_tokens:
            logger.debug(f"{account} related to {device_monitor} has {len(registration_tokens)} tokens")
            return FirebaseMessageItem(
                id=str(device_monitor.id),
                title=device_monitor.message,
                body=device_monitor.message_detail,
                data={
                    "id": str(device_monitor.id),
                    "occurred_at": str(device_monitor.occurred_at),
                    "imei": device_monitor.imei,
                },
                registration_tokens=registration_tokens,
                badge=account.badge,
            )
        else:
            logger.debug(f"{account} related to {device_monitor} has no valid token")
    else:
        logger.debug(
            f"{device_monitor} (push_firebase_message={device_monitor.push_firebase_message}) "
            f"doesn't allow to push firebase message"
        )


def create_email_items(device_monitor: DeviceMonitorModel) -> Iterable[SesEmailItem]:
    # check alert_setting is enabled for the specific monitor_case
    account = device_monitor.device.account
    if device_monitor.send_email:
        if account.alert_setting.is_email_alert_enable(device_monitor.monitor_case):
            recipients = [item.notify_user_email for item in account.notify_users if item.notify_user_email]
            logger.debug(f"{account} has {len(recipients)} recipients")

            for recipient in recipients:
                subject = EMAIL_TITLE_MAPPING.get(f"{device_monitor.monitor_case}:{device_monitor.monitor_status}")
                if device_monitor.monitor_status == MonitorStatus.ABNORMAL:
                    message_template = ABNORMAL_EMAIL_TEMPLATE
                elif device_monitor.monitor_status == MonitorStatus.NORMAL:
                    message_template = RECOVER_EMAIL_TEMPLATE
                else:
                    message_template = None

                yield SesEmailItem(
                    id=str(device_monitor.id),
                    subject=subject,
                    message=message_template.format(
                        email=recipient,
                        device_monitor_id=device_monitor.id,
                        device_name=device_monitor.device.device_name,
                        imei=device_monitor.imei,
                        occurred_at=(device_monitor.occurred_at + JST_OFFSET).strftime(DATETIME_FORMAT),
                        content=device_monitor.message_detail,
                    ),
                    recipients=[recipient],
                )

        else:
            logger.debug(f"{account.alert_setting} related to {device_monitor} doesn't allow to send email")
    else:
        logger.debug(f"{device_monitor} (send_email={device_monitor.send_email}) doesn't allow to send email")


def create_notification_items(
    device_monitors: list[DeviceMonitorModel],
) -> (list[FirebaseMessageItem], list[SesEmailItem]):
    # create SesEmailItems and FirebaseMessageItems
    firebase_messages: list[FirebaseMessageItem] = []
    ses_emails: list[SesEmailItem] = []

    for device_monitor in device_monitors:
        account = device_monitor.device.account
        # skip if the user has been deleted or disabled
        if account and account.is_enabled():
            if firebase_item := create_firebase_item(device_monitor):
                firebase_messages.append(firebase_item)
                # logger.debug(f"{device_monitor} Created items: {firebase_item}")

            if email_items := list(create_email_items(device_monitor)):
                ses_emails.extend(email_items)
                # logger.debug(f"{device_monitor} Created items: {email_items}")
        else:
            logger.debug(f"{device_monitor} {account} is disabled")
    return firebase_messages, ses_emails


def handler(event, context):
    """:param event: SQS event"""
    batch_item_failures = []
    records = event.get("Records", [])
    logger.info(f"Got {len(records)} SQS records")

    for record in records:
        try:
            # deserialize event.record
            device_monitors = deserialize_sqs_record_to_device_monitor_models(record)
            logger.info(f"Got {len(device_monitors)} device monitors: {device_monitors}")

            load_notification_info(device_monitors)
            firebase_messages, ses_emails = create_notification_items(device_monitors)
            logger.info(
                f"Created {len(firebase_messages)} FirebaseMessages: {firebase_messages}, "
                f"{len(ses_emails)} SesEmails: {ses_emails}"
            )

            notification_service.send_firebase_messages(firebase_messages)
            notification_service.send_ses_emails(ses_emails)
        except Exception as e:
            logger.error(f"Failed to process record {record} - {e}")
            batch_item_failures.append(record["messageId"])

    close_all_sessions()
    return {"batchItemFailures": batch_item_failures}
