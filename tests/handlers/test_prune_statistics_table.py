from datetime import datetime, timedelta

from mock import MagicMock

from src.handlers.prune_statistics import main
from src.models import StatisticModel
from src.repositories import StatisticRepository

statistic_repository = StatisticRepository()


def test_normal_case(dummy_device):
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # dummy data
    expired_datetime = datetime.utcnow().date() - timedelta(days=main.EXPIRED_DAYS, minutes=1)
    statistic_repository.bulk_create(
        [
            {
                "imei": dummy_device.imei,
                "sensor_time": expired_datetime - timedelta(minutes=5),
                "co2": 1000 + i,
            }
            for i in range(10)
        ]
    )
    # test
    main.handler(None, None)

    statistics = statistic_repository.list(
        StatisticModel.sensor_time <= expired_datetime, imei=dummy_device.imei, offset=0, limit=10
    )
    assert len(statistics) == 0
