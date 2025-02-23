from datetime import datetime, timedelta

from src.repositories import StatisticRepository

statistic_repository = StatisticRepository()


def test_statistic_repository(dummy_device):
    # dummy
    statistic_repository.delete_all()
    now = datetime.utcnow()
    statistic_repository.bulk_create(
        [
            {"imei": dummy_device.imei, "sensor_time": now - timedelta(minutes=10), "co2": 1000},
            {"imei": dummy_device.imei, "sensor_time": now - timedelta(minutes=5), "co2": 1000},
            {"imei": dummy_device.imei, "sensor_time": now, "co2": 1000},
        ],
        return_defaults=True,
    )
    assert len(statistic_repository.list(imei=dummy_device.imei)) == 3
    statistic_repository.delete_all()
