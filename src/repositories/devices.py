from datetime import datetime, timedelta
from typing import Iterable

from sqlalchemy import Integer, and_, cast, desc, func, or_

from src.models import AlertSettingModel, DeviceModel, StatisticModel
from src.types import DeviceState, MonitorStatus
from src.utils import parse_version

from .base import SqlExtendedRepository


class DeviceRepository(SqlExtendedRepository):
    model_class = DeviceModel

    def list_devices_by_imei(self, imeis: Iterable[str]) -> list[DeviceModel]:
        return self.query.filter(DeviceModel.imei.in_(imeis)).all()

    def list_disconnected_devices(self, offline_duration: int = 10) -> list[DeviceModel]:
        """
        :param offline_duration: the duration of time (in minutes) during which devices do not receive any updates.
        """
        offline_datetime = datetime.utcnow() - timedelta(minutes=offline_duration)
        return self.query.filter(DeviceModel.sensor_time <= offline_datetime).all()

    def list_absent_devices(self) -> list[DeviceModel]:
        """
        Get recover absent devices from `devices` table which has device_state=`ABSENCE` and
          intruder_monitor_status=`ABNORMAL`
        """
        return self.query.filter(
            and_(
                DeviceModel.device_state == DeviceState.ABSENCE,
                DeviceModel.intruder_monitor_status == MonitorStatus.ABNORMAL,
            )
        ).all()

    def load_last_statistics(self, devices: list[DeviceModel]) -> list[DeviceModel]:
        # query db to get last statistic coresponding with emei then map them to device models
        device_mapping = {device.imei: device for device in devices}
        subquery = (
            self.session.query(
                StatisticModel.id,
                StatisticModel.imei,
                StatisticModel.sensor_time,
                StatisticModel.co2_diff,
                func.row_number()
                .over(
                    partition_by=(StatisticModel.imei,),
                    order_by=desc(StatisticModel.id),
                )
                .label("row_num"),
            )
            .filter(StatisticModel.imei.in_(device_mapping.keys()))
            .subquery()
        )
        results = self.session.query(subquery).filter(subquery.c.row_num == 1).all()
        for _id, imei, sensor_time, co2_diff, *_ in results:
            device = device_mapping.get(imei)
            device.last_statistic = StatisticModel(
                id=_id,
                imei=imei,
                sensor_time=sensor_time,
                co2_diff=co2_diff,
            )
        return devices

    def load_alert_settings(self, devices: list[DeviceModel]) -> list[DeviceModel]:
        # query db to get alert_settings then map them to device models
        account_ids = (device.account_id for device in devices)
        alert_setting_mapping = dict(
            self.session.query(AlertSettingModel.account_id, AlertSettingModel).filter(
                AlertSettingModel.account_id.in_(account_ids)
            )
        )
        for device in devices:
            device.alert_setting = alert_setting_mapping.get(device.account_id)
        return devices

    @classmethod
    def message_serializer(cls, _obj):
        """Serializer for SQS & SNS message"""
        if isinstance(_obj, DeviceModel):
            return {
                "imei": _obj.imei,
                "co2": _obj.co2,
                "temp": _obj.temp,
                "humid": _obj.humid,
                "sensor_time": _obj.sensor_time,
                "updated_at": _obj.updated_at,
            }
        else:
            return cls.default_serializer(_obj)

    def list_devices_below_version(self, version: str, limit=200, offset=0) -> list[DeviceModel]:
        parsed_version = parse_version(version)

        # firmware_version is null or firmware_version < version
        separator = "."
        casted_field = (
            cast(func.substring_index(DeviceModel.firmware_version, separator, 1), Integer) * 1000000
            + cast(func.substring_index(DeviceModel.firmware_version, separator, -2), Integer) * 1000
            + cast(func.substring_index(DeviceModel.firmware_version, separator, -1), Integer)
        )
        query = (
            self.query.filter(
                or_(
                    DeviceModel.firmware_version.is_(None),
                    casted_field < parsed_version,
                )
            )
            .limit(limit)
            .offset(offset)
        )
        return query.all()
