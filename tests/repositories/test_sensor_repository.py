from datetime import datetime, timedelta

from src.repositories.sensors import SensorRepository

sensor_repository = SensorRepository()

IMEI = "350457796259260"


def test_deserialize():
    item = sensor_repository.deserialize(
        {
            "hum": {"N": "54"},
            "sensor_time": {"S": "2023-04-21 13:13:00"},
            "server_time": {"S": "2023-04-21 13:13:00"},
            "co2": {"N": "1000"},
            "topic": {"S": "/nbIMEI/data"},
            "IMEI": {"S": IMEI},
            "tem": {"N": "25.18"},
            "timestamp": {"N": "1682050426"},
        }
    )
    assert item.IMEI == IMEI
    assert item.sensor_time == datetime(2023, 4, 21, 13, 13)


def test_get_sensor(dummy_sensors):
    now = datetime.utcnow()
    time_range = (now - timedelta(hours=1), now)
    sensors = list(sensor_repository.list_by_imei(IMEI))
    assert len(sensors) >= 10
    sensors = list(sensor_repository.list_by_imei(IMEI, time_range))
    assert len(sensors) >= 10
    item = sensors[0]
    assert sensor_repository.get(item.IMEI, item.sensor_time) is not None
