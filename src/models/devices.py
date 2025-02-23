from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .alert_settings import AlertSettingModel
from .base import BaseModel
from .statistics import StatisticModel


class DeviceModel(BaseModel):
    __tablename__ = "devices"

    imei = Column(String(20), primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    device_name = Column(String(255))
    sim_id = Column(String(20))
    sim_plan = Column(String(20))
    device_state = Column(Integer, default=1)
    device_status = Column(Integer, default=2)
    firmware_version = Column(String(20))
    co2 = Column(Integer)
    temp = Column(Float)
    humid = Column(Integer)
    co2_monitor_status = Column(Integer, default=4)
    temp_monitor_status = Column(Integer, default=4)
    heat_stroke_monitor_status = Column(Integer, default=4)
    influenza_monitor_status = Column(Integer, default=4)
    long_disconnect_monitor_status = Column(Integer, default=4)
    long_absenc_monitor_status = Column(Integer, default=4)
    intruder_monitor_status = Column(Integer, default=4)
    started_at = Column(DateTime)
    expired_at = Column(DateTime)
    deleted_at = Column(DateTime)
    sensor_time = Column(DateTime)
    is_push = Column(Integer, default=1)
    # relationship
    device_monitors = relationship(
        "DeviceMonitorModel",
        lazy=True,
        uselist=True,
        primaryjoin="DeviceModel.imei == DeviceMonitorModel.imei",
        backref="device",
    )
    account = relationship("AccountModel", lazy=True, uselist=False)

    # custom attribute
    _alert_setting = None
    _last_statistic = None

    @property
    def alert_setting(self):
        return self._alert_setting

    @alert_setting.setter
    def alert_setting(self, value):
        if isinstance(value, AlertSettingModel):
            self._alert_setting = value
        elif isinstance(value, dict):
            self._alert_setting = AlertSettingModel(**value)

    @property
    def last_statistic(self):
        return self._last_statistic

    @last_statistic.setter
    def last_statistic(self, value):
        if isinstance(value, StatisticModel):
            self._last_statistic = value
        elif isinstance(value, dict):
            self._last_statistic = StatisticModel(**value)

    def __repr__(self):
        return f"Device<imei={self.imei}>"
