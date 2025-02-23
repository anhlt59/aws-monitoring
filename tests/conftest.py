import os
import sys
from datetime import datetime, timedelta

import pytest
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(BASE_DIR))
load_dotenv(os.path.join(BASE_DIR, ".env.local"))

from src.models import (  # noqa
    AlertSettingModel,
    DeviceModel,
    DeviceMonitorModel,
    DeviceTokenModel,
    NotifyUserDeviceModel,
    NotifyUserModel,
    StatisticModel,
)
from src.repositories import (  # noqa
    AccountRepository,
    AlertSettingRepository,
    DeviceMonitorReadRepository,
    DeviceMonitorRepository,
    DeviceRepository,
    DeviceTokenRepository,
    NotifyUserDeviceRepository,
    NotifyUserRepository,
    engine,
)
from src.repositories.base import BaseModel  # noqa
from src.repositories.sensors import SensorRepository  # noqa

# create sql tables if they are not exist
# BaseModel.metadata.drop_all(engine)
BaseModel.metadata.create_all(engine)

account_repository = AccountRepository()
alert_setting_repository = AlertSettingRepository()
device_repository = DeviceRepository()
device_monitor_repository = DeviceMonitorRepository()
device_monitor_read_repository = DeviceMonitorReadRepository()
device_token_repository = DeviceTokenRepository()
notify_user_repository = NotifyUserRepository()
notify_user_device_repository = NotifyUserDeviceRepository()
sensor_repository = SensorRepository()

IMEI = "350457796259260"
IMEI2 = "350457796259261"
SIM_ID = "8942310221008800007"
ACCOUNT_ID = 1
DEVICE_DATA = {
    "imei": IMEI,
    "device_name": "DUMMY_DEVICE",
    "account_id": None,
    "sim_id": SIM_ID,
    "firmware_version": "0.0.018",
    "device_state": 1,
    "device_status": 4,
    "co2_monitor_status": 4,
    "temp_monitor_status": 4,
    "heat_stroke_monitor_status": 4,
    "influenza_monitor_status": 4,
    "long_disconnect_monitor_status": 4,
    "long_absenc_monitor_status": 4,
    "intruder_monitor_status": 4,
    "co2": 3000,
    "temp": 30,
    "humid": 100,
    "sensor_time": datetime.utcnow(),
}
DEVICE_MONITOR_DATA = {
    "imei": IMEI,
    "occurred_at": datetime.utcnow(),
    "monitor_status": 1,
    "monitor_case": 1,
    "message": "unittest",
    "message_detail": "test from local",
    "push_firebase_message": True,
    "send_email": True,
}


@pytest.fixture
def dummy_account():
    if accounts := account_repository.list():
        yield accounts[0]
    else:
        yield account_repository.create({"role": 1})


@pytest.fixture
def dummy_device(dummy_account):
    data = {**DEVICE_DATA, "account_id": dummy_account.id, "imei": IMEI}
    if device_repository.get(IMEI):
        device = device_repository.update(IMEI, data)
    else:
        device = device_repository.create(data)
    yield device
    # device_repository.delete_all()


@pytest.fixture
def dummy_soracom_devices(dummy_account):
    soracom_devices = [
        {
            **DEVICE_DATA,
            "account_id": dummy_account.id,
            "imei": "350457796259263",
            "sim_id": "8942310221008817100",
            "sensor_time": datetime.utcnow() - timedelta(minutes=15),
        },
        {
            **DEVICE_DATA,
            "account_id": dummy_account.id,
            "imei": "350457796260360",
            "sim_id": "8942310221008814677",
            "sensor_time": datetime.utcnow() - timedelta(minutes=15),
        },
        {**DEVICE_DATA, "account_id": dummy_account.id, "imei": "350457796260592", "sim_id": "8942310221008814388"},
    ]
    devices = []
    for item in soracom_devices:
        if device_repository.get(item["imei"]):
            devices.append(device_repository.update(item["imei"], item))
        else:
            devices.append(device_repository.create(item))
    yield devices


@pytest.fixture
def dummy_abnormal_device(dummy_account):
    data = {
        **DEVICE_DATA,
        "account_id": dummy_account.id,
        "co2": 4000,
        "sensor_time": datetime.utcnow() - timedelta(days=1),
    }
    if device_repository.get(IMEI):
        device = device_repository.update(IMEI, data)
    else:
        device = device_repository.create(data)
    yield device


@pytest.fixture
def dummy_device_monitor(dummy_device):
    data = {**DEVICE_MONITOR_DATA, "imei": IMEI}
    item = device_monitor_repository.create(data)
    yield item
    device_monitor_repository.delete_all()


@pytest.fixture
def dummy_device_monitor_read(dummy_account, dummy_device_monitor):
    data = {"account_id": dummy_account.id, "monitor_id": dummy_device_monitor.id}
    item = device_monitor_read_repository.create(data)
    yield item
    device_monitor_read_repository.delete_all()


@pytest.fixture
def dummy_device_token(dummy_account):
    token = device_token_repository.create(
        {
            "account_id": dummy_account.id,
            "device_token": "cMhtMG84T8WwVXW0F_4JEW:APA91bFzVvZLuGNxNOpaE20_GiB1-9paY4ZtCzMUI29kWJ6IQJTzAyrI7h2WlBmA5"
            "YwSnHuGnf0qpGiRCT8vprACfC6R5auY4qXkxpOudqcUjudGXwezbnl_LMiOeatbxoPeTdFJ0X-y",
        }
    )
    yield token
    device_token_repository.delete_all()


@pytest.fixture
def dummy_alert_setting(dummy_account):
    setting = alert_setting_repository.get_by(account_id=dummy_account.id)
    if not setting:
        setting = alert_setting_repository.create({"account_id": dummy_account.id, "long_absenc_alert_time": 2})
    yield setting
    alert_setting_repository.delete_all()


@pytest.fixture
def dummy_notify_user(dummy_account):
    notify_user = notify_user_repository.create(
        {
            "account_id": dummy_account.id,
            "notify_user_email": "denaribots-01@yopmail.com",
            "notify_user_name": "test-01",
        }
    )
    yield notify_user
    notify_user_repository.delete_all()


@pytest.fixture
def dummy_notify_user_device(dummy_device, dummy_notify_user):
    notify_user_device = notify_user_device_repository.create(
        {
            "imei": dummy_device.imei,
            "notify_user_id": dummy_notify_user.id,
        }
    )
    yield notify_user_device
    notify_user_device_repository.delete_all()


@pytest.fixture
def dummy_sensor(dummy_device):
    item = sensor_repository.create(
        {
            "IMEI": IMEI,
            "sensor_time": datetime.utcnow(),
            "co2": 100,
            "hum": 100,
            "tem": 100,
            "topic": f"/nb/{IMEI}/data",
        }
    )
    yield item
    item.delete()


@pytest.fixture
def dummy_sensors(dummy_device):
    now = datetime.utcnow()
    items = sensor_repository.bulk_create(
        [
            {
                "IMEI": IMEI,
                "topic": f"/nb/{IMEI}/data",
                "co2": 4000 + i,
                "hum": 50 + i,
                "tem": 20 + i,
                "sensor_time": now - timedelta(minutes=i * 5),
            }
            for i in range(10)
        ]
    )
    yield items
    for item in items:
        item.delete()
