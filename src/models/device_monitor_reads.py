from sqlalchemy import Column, ForeignKey, Index, Integer

from src.models.base import Base


class DeviceMonitorReadModel(Base):
    __tablename__ = "device_monitor_reads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    monitor_id = Column(Integer, ForeignKey("device_monitors.id"))

    __table_args__ = (Index("account_monitor_idx", "account_id", "monitor_id"),)

    def __repr__(self):
        return f"DeviceMonitorRead<id={self.id}>"
