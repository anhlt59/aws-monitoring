from typing import Iterable

from src.models import AlertSettingModel

from .base import SqlRepository


class AlertSettingRepository(SqlRepository):
    model_class = AlertSettingModel

    def list_by_account_ids(self, account_ids: Iterable[int]) -> list[AlertSettingModel]:
        return self.query.filter(AlertSettingModel.account_id.in_(account_ids)).all()
