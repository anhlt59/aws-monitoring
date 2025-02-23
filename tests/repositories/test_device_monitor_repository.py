from src.repositories import DeviceMonitorRepository
from src.types import MonitorCases

device_monitor_repository = DeviceMonitorRepository()


def test_device_monitor_repository(dummy_device_monitor):
    device_monitor_repository.bulk_update([{"id": dummy_device_monitor.id, "monitor_status": 4}])
    updated_item = device_monitor_repository.get(dummy_device_monitor.id)
    assert updated_item.monitor_status == 4
    assert len(device_monitor_repository.list(imei=dummy_device_monitor.imei)) == 1

    # test `get_last_device_monitor`
    assert (
        device_monitor_repository.get_last_device_monitors([dummy_device_monitor.imei], [MonitorCases.CO2]) is not None
    )
    assert (
        device_monitor_repository.get_last_device_monitor(dummy_device_monitor.imei, dummy_device_monitor.monitor_case)
        is not None
    )
