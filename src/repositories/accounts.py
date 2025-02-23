from sqlalchemy import and_, func
from sqlalchemy.orm import joinedload

from src.models import AccountModel, DeviceModel, DeviceMonitorModel, DeviceMonitorReadModel
from src.types import MonitorStatus

from .base import SqlRepository


class AccountRepository(SqlRepository):
    model_class = AccountModel

    def list_accounts_with_notification_info(self, ids: list[int]) -> list[AccountModel]:
        accounts = (
            self.query.options(
                joinedload(AccountModel.device_tokens),
                joinedload(AccountModel.alert_setting),
            )
            .filter(AccountModel.id.in_(ids))
            .all()
        )

        if account_ids_to_get_badge := [account.id for account in accounts if account.device_tokens]:
            subquery = (
                self.session.query(
                    DeviceMonitorModel.id.label("device_monitor_id"),
                    DeviceModel.account_id.label("account_id"),
                    DeviceMonitorReadModel.id.label("device_monitor_read_id"),
                )
                .join(DeviceModel)
                .outerjoin(DeviceMonitorReadModel)
                .filter(
                    and_(
                        DeviceModel.account_id.in_(account_ids_to_get_badge),
                        DeviceModel.deleted_at.is_(None),
                        DeviceMonitorModel.monitor_status.in_([MonitorStatus.WARNING, MonitorStatus.ABNORMAL]),
                        DeviceMonitorReadModel.id.is_(None),
                    )
                )
                .subquery()
            )

            badge_counts = (
                self.session.query(
                    subquery.c.account_id,
                    func.count(),
                )
                .group_by(subquery.c.account_id)
                .all()
            )

            # update the badge attribute of accounts
            mapping = {account_id: badge_count for account_id, badge_count in badge_counts}
            for account in accounts:
                account.badge = mapping.get(account.id, 0)

        return accounts
