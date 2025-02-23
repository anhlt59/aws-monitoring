from src.models import NotifyUserDeviceModel, NotifyUserModel

from .base import SqlRepository


class NotifyUserRepository(SqlRepository):
    model_class = NotifyUserModel

    def list_notify_users_by_account_id_and_imei(
        self, account_ids: list[int], imeis: list[str]
    ) -> list[NotifyUserModel]:
        return (
            self.session.query(NotifyUserDeviceModel.imei, NotifyUserModel)
            .join(NotifyUserDeviceModel, NotifyUserModel.id == NotifyUserDeviceModel.notify_user_id)
            .filter(NotifyUserDeviceModel.imei.in_(imeis))
            .filter(NotifyUserModel.account_id.in_(account_ids))
            .all()
        )
