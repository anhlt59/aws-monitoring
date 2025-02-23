from src.repositories import AlertSettingRepository

alert_setting_repository = AlertSettingRepository()


def test_alert_setting_repository(dummy_alert_setting):
    # test
    assert alert_setting_repository.get_by(account_id=dummy_alert_setting.account_id) is not None
    assert len(alert_setting_repository.list(account_id=dummy_alert_setting.account_id)) == 1
    assert len(alert_setting_repository.list_by_account_ids(account_ids=[dummy_alert_setting.account_id])) == 1
