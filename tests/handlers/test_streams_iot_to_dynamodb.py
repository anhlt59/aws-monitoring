import json

from src.handlers.stream_iot_to_dynamodb import main
from src.repositories.sensors import SensorRepository

IMEI = "350457796259260"
sensor_repository = SensorRepository()


def clear():
    # clear
    for item in sensor_repository.model_class.scan():
        item.delete()


def test_handler_insert_sensor(dummy_device):
    # dummy
    event = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "body": json.dumps(
                    {
                        "event": 0,
                        "co2": 1019 + i,
                        "tem": 27.78 + i,
                        "hum": 50 + i,
                        "time": "20230727083103",
                        "topic": f"/nb/{350457796259260 + i}/data",
                    }
                ),
            }
            for i in range(10)
        ]
    }
    # test
    result = main.handler(event, None)
    sensor = sensor_repository.get(IMEI, "2023-07-26 23:31:03")
    assert sensor is not None
    assert not result["batchItemFailures"]

    clear()


def test_handler_device_not_found():
    # dummy
    item = {
        "event": 0,
        "co2": 1019,
        "tem": 27.78,
        "hum": 50,
        "time": "20230727083103",
        "topic": f"/nb/{IMEI}/data",
    }
    event = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "body": json.dumps(item),
            }
        ]
    }
    # test
    result = main.handler(event, None)
    assert sensor_repository.get(IMEI, "2023-07-26 23:31:03")
    assert not result["batchItemFailures"]

    clear()


def test_invalid_event():
    # dummy
    event = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "body": json.dumps(
                    {
                        "event": 0,
                        "time": "20230727083103",
                        "topic": f"/nb/{350457796259260}/data",
                    }
                ),
            }
        ]
    }
    # test
    result = main.handler(event, None)
    assert not result["batchItemFailures"]

    sensors = list(sensor_repository.model_class.scan())
    assert len(sensors) == 0

    clear()
