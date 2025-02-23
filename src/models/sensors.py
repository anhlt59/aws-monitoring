from datetime import datetime, timedelta

from pynamodb.attributes import NumberAttribute, UnicodeAttribute
from pynamodb.models import Model

from src.constants import AWS_ENDPOINT, AWS_REGION, DATETIME_FORMAT, DYNAMODB_TABLE


def get_server_time():
    return datetime.utcnow().strftime(DATETIME_FORMAT)


def get_expired_time():
    return round((datetime.utcnow() + timedelta(days=365)).timestamp())


class KeyAttribute(UnicodeAttribute):
    prefix: str

    def __init__(self, prefix: str, **kwargs):
        super().__init__(**kwargs)
        self.prefix = prefix

    def serialize(self, value: str):
        return super().serialize(f"{self.prefix}#{value}")

    def deserialize(self, value: str):
        value = value.replace(f"{self.prefix}#", "")
        return super().deserialize(value)


class StringDatetimeAttribute(UnicodeAttribute):
    datetime_format: str

    def __init__(self, datetime_format: str = DATETIME_FORMAT, **kwargs):
        super().__init__(**kwargs)
        self.datetime_format = datetime_format

    def serialize(self, value: datetime | str) -> str:
        if isinstance(value, datetime):
            value = value.strftime(self.datetime_format)
        return super().serialize(value)

    def deserialize(self, value: str | datetime) -> datetime:
        if not isinstance(value, datetime):
            value = super().deserialize(value)
            value = datetime.strptime(value, self.datetime_format)
        return value


class SensorModel(Model):
    class Meta:
        host = AWS_ENDPOINT
        region = AWS_REGION
        table_name = DYNAMODB_TABLE
        read_timeout_seconds = 3

    IMEI = UnicodeAttribute(hash_key=True)
    sensor_time = StringDatetimeAttribute(range_key=True)
    server_time = StringDatetimeAttribute(default_for_new=get_server_time)
    expired_at = NumberAttribute(default_for_new=get_expired_time, null=True)
    co2 = NumberAttribute()
    hum = NumberAttribute()
    tem = NumberAttribute()
    topic = UnicodeAttribute()

    # custom attributes
    message_id: str = ""

    def __repr__(self):
        return f"Sensor<imei={self.IMEI}, sensor_time={self.sensor_time}>"
