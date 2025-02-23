from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


# Enums ---------------------------------------------------------------
class AccountStatus:
    ENABLE = 1
    DISABLE = 2


class EnableStatus:
    DISABLE = 0
    ENABLE = 1


class MonitorStatus:
    NORMAL = 1
    WARNING = 2
    ABNORMAL = 3
    UNKNOWN = 4


class DeviceState:
    MONITORING = 1
    ABSENCE = 2
    STOP_MONITORING = 3


class DeviceStatus:
    NO_SYSTEM_REGISTRATION = 1
    NO_REGISTRATION = 2
    OFFLINE = 3
    ONLINE = 4
    ABNORMAL = 5
    UNKNOWN = 6


class MonitorCases:
    CO2 = 1
    TEMPERATURE = 2
    HEATSTROKE = 3
    INFLUENZA = 4
    LONG_TERM_ABSENCE = 5
    LONG_TERM_DISCONNECT = 6
    SUSPICIOUS_INTRUDER = 7


MONITOR_CASES = {
    1: "co2_email_alert",
    2: "temp_email_alert",
    3: "heat_stroke_email_alert",
    4: None,
    5: "long_absenc_email_alert",
    6: "long_disconnect_email_alert",
    7: "intruder_email_alert",
}


# Alert Settings
class MonitoringThresholds:
    # monitoring case #1
    CO2_WARNING = 1500
    CO2_ABNORMAL = 3000
    # monitoring case #2
    TEMP_WARNING = 35
    TEMP_ABNORMAL = 50
    # monitoring case #3
    HEATSTROKE_HUMID_WARNING = 60
    HEATSTROKE_TEMP_WARNING = 28
    HEATSTROKE_TEMP_ABNORMAL = 32
    # monitoring case #4
    INFLUENZA_TEMP = 18
    INFLUENZA_HUM = 40
    # monitoring case #5,6
    CO2_DIFF = 35
    # monitoring case #7
    RECOVERY_CONNECTION_DURATION = 600  # 10 minutes converted in seconds
    APP_NOTIFICATION_DISCONNECT_DURATION = 1800  # 30 minutes converted to seconds
    EMAIL_NOTIFICATION_DISCONNECT_DURATION = 86400  # 24h converted to in seconds


# DATA TYPES ----------------------------------------------------------
@dataclass(slots=True)
class SqsMessage:
    message_body: str
    message_attributes: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))

    def __repr__(self):
        return f"SqsMessage(Id='{self.id}')"


@dataclass(slots=True)
class SesEmailItem:
    subject: str
    message: str
    recipients: list[str]
    id: str = field(default_factory=lambda: str(uuid4()))

    def __repr__(self):
        return f"SesEmail(id='{self.id}', subject='{self.subject}, recipients={self.recipients})"


@dataclass(slots=True)
class FirebaseMessageItem:
    title: str
    body: str
    registration_tokens: list[str]
    data: dict | None = None
    badge: int | None = None
    id: str = field(default_factory=lambda: str(uuid4()))

    def __repr__(self):
        return (
            f"FirebaseMessage(id='{self.id}', title='{self.title}',"
            f"registration_tokens={[f'{i:.20}...' for i in self.registration_tokens]})"
        )
