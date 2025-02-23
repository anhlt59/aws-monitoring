from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class DeviceMonitorModel(BaseModel):
    __tablename__ = "device_monitors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    imei = Column(String(20), ForeignKey("devices.imei"))
    occurred_at = Column(DateTime)
    monitor_case = Column(Integer)
    monitor_status = Column(Integer)
    message = Column(String(50))
    message_detail = Column(String(255))
    memo = Column(String(50))
    created_by = Column(Integer, default=0)
    updated_by = Column(Integer, default=0, onupdate=0)

    device_monitor_read = relationship("DeviceMonitorReadModel", backref="device_monitor", lazy=True, uselist=False)

    __table_args__ = (Index("imei_monitor_idx", "imei", "monitor_case", "monitor_status"),)

    # custom attributes
    push_firebase_message = False
    send_email = False
    allow_notification = False

    def to_dict(self, **kwargs) -> dict:
        item = super().to_dict(**kwargs)
        item.update(
            push_firebase_message=self.push_firebase_message,
            send_email=self.send_email,
        )
        return item

    def __repr__(self):
        return f"DeviceMonitor<id={self.id}, imei={self.imei}>"
