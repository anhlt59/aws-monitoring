from src.repositories import DeviceTokenRepository

device_token_repository = DeviceTokenRepository()


def test_device_token_repository(dummy_device_token):
    # test
    assert device_token_repository.get_by(account_id=dummy_device_token.account_id) is not None
    assert len(device_token_repository.list(account_id=dummy_device_token.account_id)) == 1
