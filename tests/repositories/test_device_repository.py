from datetime import datetime, timedelta

from src.repositories import DeviceRepository, StatisticRepository

device_repository = DeviceRepository()
statistic_repository = StatisticRepository()


def test_device_repository(dummy_device):
    device_repository.update(dummy_device.imei, {"device_name": "UPDATED"})
    device_repository.bulk_update([{"imei": dummy_device.imei, "co2": 10000}])
    updated_item = device_repository.get(dummy_device.imei)
    assert device_repository.get_by(sim_id=dummy_device.sim_id) is not None
    assert len(device_repository.list(imei=dummy_device.imei)) == 1
    assert len(device_repository.list_devices_by_imei(imeis=[dummy_device.imei])) == 1
    assert updated_item.device_name == "UPDATED"
    assert updated_item.co2 == 10000

    # disconnected devices
    assert len(device_repository.list_disconnected_devices()) == 0
    dummy_device.sensor_time = datetime.utcnow() - timedelta(days=1)
    device_repository.save(dummy_device)
    assert len(device_repository.list_disconnected_devices()) == 1
