from sqlalchemy import Column, ForeignKey, Integer

from src.types import MONITOR_CASES, EnableStatus

from .base import BaseModel


class AlertSettingModel(BaseModel):
    __tablename__ = "alert_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), index=True)
    co2_email_alert = Column(Integer, default=1)
    temp_email_alert = Column(Integer, default=1)
    heat_stroke_email_alert = Column(Integer, default=1)
    long_disconnect_email_alert = Column(Integer, default=1)
    intruder_email_alert = Column(Integer, default=1)
    long_absenc_email_alert = Column(Integer, default=1)
    long_absenc_alert_time = Column(Integer, default=48)

    def is_email_alert_enable(self, monitor_case: int):
        if field_name := MONITOR_CASES.get(monitor_case):
            return getattr(self, field_name) == EnableStatus.ENABLE
        return False

    def __repr__(self):
        return f"AlertSetting<id={self.id}, account_id={self.account_id}>"
