from src.repositories import NotifyUserRepository

IMEI = "350457796259260"

notify_user_repository = NotifyUserRepository()


def test_get_notify_user(dummy_notify_user):
    assert notify_user_repository.get_by(account_id=dummy_notify_user.account_id) is not None
    assert len(notify_user_repository.list(account_id=dummy_notify_user.account_id)) == 1
