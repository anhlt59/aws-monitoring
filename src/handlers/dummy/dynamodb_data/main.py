import time
from datetime import datetime
from random import randint

from src.handlers.dummy.common import IMEIS
from src.logger import logger
from src.models.sensors import SensorModel
from src.repositories.sensors import SensorRepository
from src.utils import chunks, round_n_minutes

CHUNK_SIZE = 25
LIMIT = 100
DELAY = 0.5  # in seconds

sensor_repository = SensorRepository()


def generate_sensors(imeis: str):
    sensor_time = round_n_minutes(datetime.utcnow(), 5)
    for imei in imeis:
        yield SensorModel(
            IMEI=imei,
            sensor_time=sensor_time,
            topic=f"/nb/{imei}/data",
            co2=3500 + (sensor_time.minute - 30) * 100 + randint(0, 500),  # nosec
            tem=20 + randint(0, 10),  # nosec
            hum=40 + randint(0, 10),  # nosec
        )


def handler(event, context):
    imeis = IMEIS[-LIMIT:]

    try:
        sensors = generate_sensors(imeis)
        for items in chunks(sensors, CHUNK_SIZE):
            sensor_repository.bulk_create(models=items)
            logger.debug(f"Created {len(items)} sensors: {items}")
            time.sleep(DELAY)
    except Exception as e:
        logger.error(f"Failed: {e}")
