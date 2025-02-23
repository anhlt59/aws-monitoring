from src.repositories import AccountRepository, DeviceMonitorRepository

account_repository = AccountRepository()
device_monitor_repository = DeviceMonitorRepository()

IMEI = "350457796259260"


def test_account_repository(dummy_account, dummy_alert_setting, dummy_device_token, dummy_device_monitor_read):
    # dummy
    device_monitors = device_monitor_repository.bulk_create(
        [
            {
                "imei": IMEI,
                "monitor_status": 3,
                "monitor_case": 1,
            }
            for _ in range(3)
        ]
    )
    # test
    accounts = account_repository.list_accounts_with_notification_info([dummy_account.id])
    assert accounts[0].badge == len(device_monitors)
    assert account_repository.get_by(id=dummy_account.id) is not None
    assert len(account_repository.list(id=dummy_account.id)) == 1
