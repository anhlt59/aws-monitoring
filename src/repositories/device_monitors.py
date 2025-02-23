from typing import Iterable

from sqlalchemy import desc, func, select
from sqlalchemy.orm import joinedload

from src.models import DeviceMonitorModel
from src.types import MonitorCases

from .base import SqlExtendedRepository


class DeviceMonitorRepository(SqlExtendedRepository):
    model_class = DeviceMonitorModel

    def list_by_id(self, ids: Iterable[int]) -> list[DeviceMonitorModel]:
        return self.query.filter(DeviceMonitorModel.id.in_(ids)).all()

    def verify_device_monitors(self, device_monitors: list[DeviceMonitorModel]) -> list[DeviceMonitorModel]:
        verified_device_monitors = (
            self.query.options(joinedload(DeviceMonitorModel.device))
            .filter(DeviceMonitorModel.id.in_(item.id for item in device_monitors))
            .all()
        )
        mapping = {item.id: item for item in verified_device_monitors}

        for item in device_monitors:
            if ref_item := mapping.get(item.id):
                ref_item.push_firebase_message = item.push_firebase_message
                ref_item.send_email = item.send_email
            else:
                self.logger.warning(f"{item} is invalid: Device<imei={item.imei}> not found")
        return verified_device_monitors

    def get_last_device_monitor(
        self, imei: str, monitor_case: MonitorCases | None = None
    ) -> DeviceMonitorModel | None:
        query = self.query.filter(DeviceMonitorModel.imei == imei)
        if monitor_case:
            query = query.filter(DeviceMonitorModel.monitor_case == monitor_case)
        return query.order_by(desc(DeviceMonitorModel.id)).first()

    def get_n_last_device_monitor(
        self, imei: str, monitor_case: MonitorCases | None = None, n: int = 1
    ) -> DeviceMonitorModel | None:
        # n = 1 means the sencond item in reverse order
        query = self.query.filter(DeviceMonitorModel.imei == imei)
        if monitor_case:
            query = query.filter(DeviceMonitorModel.monitor_case == monitor_case)
        return query.order_by(desc(DeviceMonitorModel.id)).offset(n).limit(1).first()

    def get_last_device_monitors(
        self, imeis: list[str] | None = None, monitor_cases: list[MonitorCases] | None = None
    ) -> Iterable[DeviceMonitorModel]:
        # build subquery
        subquery = select(
            DeviceMonitorModel.id,
            DeviceMonitorModel.imei,
            DeviceMonitorModel.monitor_case,
            DeviceMonitorModel.monitor_status,
            DeviceMonitorModel.occurred_at,
            func.row_number()
            .over(
                partition_by=(DeviceMonitorModel.imei, DeviceMonitorModel.monitor_case),
                order_by=desc(DeviceMonitorModel.id),
            )
            .label("row_num"),
        )
        if imeis:
            subquery = subquery.filter(DeviceMonitorModel.imei.in_(imeis))
        if monitor_cases:
            subquery = subquery.filter(DeviceMonitorModel.monitor_case.in_(monitor_cases))
        subquery = subquery.subquery()

        # build query depends on the subquery
        results = self.session.query(subquery).filter(subquery.c.row_num == 1).all()
        return (
            DeviceMonitorModel(
                id=item[0], imei=item[1], monitor_case=item[2], monitor_status=item[3], occurred_at=item[4]
            )
            for item in results
        )
