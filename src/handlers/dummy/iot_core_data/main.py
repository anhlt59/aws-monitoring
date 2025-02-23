import json
from datetime import datetime, timedelta
from random import randint

from src.constants import PARSE_TIME_FORMAT
from src.handlers.dummy.common import IMEIS
from src.logger import logger
from src.services.iot_core import IotDataService
from src.utils import chunks, round_n_minutes

IMEI_LIMIT = 3000
CHUNK_LIMIT = 100

iot_service = IotDataService()


def generate_sensors(imeis: str):
    sensor_time = round_n_minutes(datetime.utcnow() + timedelta(hours=9), 5)
    for imei in imeis:
        yield {
            "event": 0,
            "co2": 3500 + (sensor_time.minute - 30) * 100 + randint(0, 500),  # nosec
            "tem": randint(10, 55),  # nosec
            "hum": randint(40, 60),  # nosec
            "time": sensor_time.strftime(PARSE_TIME_FORMAT),
            "topic": f"/nb/{imei}/data",
        }


def handler(event, context):
    imeis = IMEIS[:IMEI_LIMIT]
    sensors = generate_sensors(imeis)

    for items in chunks(sensors, CHUNK_LIMIT):
        try:
            for item in items:
                iot_service.publish(topic=item["topic"], payload=json.dumps(item))
            logger.debug(f"Pushlished {CHUNK_LIMIT} messages")
        except Exception as e:
            logger.error(f"Failed: {e}")
