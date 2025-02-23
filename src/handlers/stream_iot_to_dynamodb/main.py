import json
from datetime import datetime, timedelta, timezone

from src.constants import PARSE_TIME_FORMAT
from src.logger import logger
from src.models.sensors import SensorModel
from src.repositories.sensors import PutItemError, SensorRepository
from src.utils import get_imei_from_topic

sensor_repository = SensorRepository()

# Asia/Tokyo timezone
TIMEZONE = timezone(timedelta(hours=9))
# batch size limit
BATCH_SIZE = 25


def deserialize_records(records: list[dict]):
    setids = set()

    for record in records:
        try:
            item = json.loads(record.get("body", "null"))
            imei = get_imei_from_topic(item.get("topic"))
            event_type = item.get("event")

            if imei and event_type == 0:
                sensor_time = datetime.strptime(item.get("time"), PARSE_TIME_FORMAT).replace(tzinfo=TIMEZONE)
                sensor_utctime = sensor_time.astimezone(timezone.utc)

                _id = f"{imei}{sensor_utctime}"
                if _id in setids:
                    logger.warning(f"Got duplicated Sensor<imei={imei}, sensor_time={sensor_utctime}>")
                    continue

                setids.add(_id)
                sensor = SensorModel(
                    IMEI=imei,
                    sensor_time=sensor_utctime,
                    co2=item.get("co2"),
                    tem=item.get("tem"),
                    hum=item.get("hum"),
                    topic=item.get("topic"),
                )
                sensor.message_id = record["messageId"]
                # logger.debug(f"Deserialized {sensor}: {sensor.to_json()}")
                yield sensor
            else:
                logger.error(f"Invalid record <`imei`={imei}, `event`={event_type}>: {item}")
        except Exception as e:
            logger.error(f"Failed to deserialize record: {e}")


def handler(event, context):
    batch_item_failures = []
    records = event.get("Records", [])
    logger.info(f"Got {len(records)} SQS records")

    try:
        sensors = list(deserialize_records(records))
        sensor_repository.bulk_create(models=sensors)
        # logger.info(f"Inserted {len(sensors)} successfully: {sensors}")
    except PutItemError as e:
        batch_item_failures.append(item.message_id for item in e.failed_items)
        logger.error(f"Failed to insert {len(e.failed_items)} items: {e}, failed_items: {e.failed_items}")
    except Exception as e:
        logger.error(f"Can't perform put action: {e}")

    return {"batchItemFailures": batch_item_failures}
