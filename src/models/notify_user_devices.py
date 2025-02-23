from sqlalchemy import Column, ForeignKey, Index, Integer, String

from .base import Base


class NotifyUserDeviceModel(Base):
    __tablename__ = "notify_user_devices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    notify_user_id = Column(Integer, ForeignKey("notify_users.id"))
    imei = Column(String(20), ForeignKey("devices.imei"))

    __table_args__ = (Index("imei_notiuser_idx", "imei", "notify_user_id"),)

    def __repr__(self):
        return f"NotifyUserDevice<id={self.id}, imei={self.imei}"
