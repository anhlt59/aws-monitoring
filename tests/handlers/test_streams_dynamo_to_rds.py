from datetime import datetime, timedelta

from mock import MagicMock

from src.constants import (
    DATETIME_FORMAT,
    SQS_MONITOR_4_URL,
    SQS_MONITOR_5_URL,
    SQS_MONITOR_6_URL,
    SQS_MONITOR_7_URL,
    SQS_MONITOR_123_URL,
    SQS_NOTIFICATION_URL,
)
from src.handlers.stream_dynamo_to_rds import main
from src.repositories import AlertSettingRepository, DeviceRepository, StatisticRepository
from src.services.sqs import SqsService

IMEI = "350457796259260"
SENSORTIME = datetime.utcnow().strftime(DATETIME_FORMAT)

alert_setting_repository = AlertSettingRepository()
device_repository = DeviceRepository()
sqs_service = SqsService()
statistic_repository = StatisticRepository()


def clear():
    # clear data
    statistic_repository.delete_all()
    for queue_url in (
        SQS_MONITOR_123_URL,
        SQS_MONITOR_4_URL,
        SQS_MONITOR_5_URL,
        SQS_MONITOR_6_URL,
        SQS_MONITOR_7_URL,
        SQS_NOTIFICATION_URL,
    ):
        sqs_service.client.purge_queue(QueueUrl=queue_url)


def test_handler(dummy_device, dummy_alert_setting):
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # dummy
    statistic_repository.create(
        {
            "imei": dummy_device.imei,
            "co2": 1010,
            "sensor_time": datetime.utcnow() - timedelta(minutes=21),
        }
    )
    device_repository.update(dummy_device.imei, {"sensor_time": datetime.utcnow() - timedelta(minutes=5)})
    event = {
        "Records": [
            {
                "eventID": "bdab5026a5d6709a9574bc7327d10004",
                "eventName": "INSERT",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "ap-southeast-1",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1690253421,
                    "Keys": {
                        "sensor_time": {"S": SENSORTIME},
                        "IMEI": {"S": IMEI},
                    },
                    "NewImage": {
                        "hum": {"N": "54"},
                        "sensor_time": {"S": SENSORTIME},
                        "server_time": {"S": SENSORTIME},
                        "co2": {"N": "1000"},
                        "topic": {"S": f"/nb/{IMEI}/data"},
                        "IMEI": {"S": IMEI},
                        "tem": {"N": "25.18"},
                    },
                    "StreamViewType": "NEW_IMAGE",
                },
            }
        ]
    }

    # test
    main.handler(event, None)
    device = device_repository.get(dummy_device.imei)
    statistic = statistic_repository.get_last_statistic(imei=dummy_device.imei)
    assert device.co2 == 1000
    assert statistic and statistic.co2 == 1000 and statistic.co2_diff == -10
    clear()


def test_handler_2(dummy_device, dummy_alert_setting):
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # dummy
    device_repository.update(dummy_device.imei, {"sensor_time": datetime.utcnow() - timedelta(seconds=300)})
    event = {
        "Records": [
            {
                "eventID": "bdab5026a5d6709a9574bc7327d10004",
                "eventName": "INSERT",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "ap-southeast-1",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1690253421,
                    "Keys": {
                        "sensor_time": {"S": SENSORTIME},
                        "IMEI": {"S": IMEI},
                    },
                    "NewImage": {
                        "hum": {"N": "54"},
                        "sensor_time": {"S": SENSORTIME},
                        "server_time": {"S": SENSORTIME},
                        "co2": {"N": "4250"},
                        "topic": {"S": f"/nb/{IMEI}/data"},
                        "IMEI": {"S": IMEI},
                        "tem": {"N": "25.18"},
                    },
                    "StreamViewType": "NEW_IMAGE",
                },
            }
        ]
    }

    # test
    main.handler(event, None)
    device = device_repository.get(dummy_device.imei)
    statistic = statistic_repository.get_by(imei=dummy_device.imei)
    assert device.co2 == 4250
    assert statistic and statistic.co2 == 4250
    clear()
