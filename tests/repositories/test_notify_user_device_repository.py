from src.repositories import NotifyUserDeviceRepository, NotifyUserRepository

notify_user_device_repository = NotifyUserDeviceRepository()
notify_user_repository = NotifyUserRepository()


def test_notify_user_device_repository(dummy_notify_user_device):
    assert notify_user_device_repository.get_by(imei=dummy_notify_user_device.imei) is not None
    assert len(notify_user_device_repository.list(imei=dummy_notify_user_device.imei)) == 1
