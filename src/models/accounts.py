from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import relationship

from src.types import AccountStatus

from .base import BaseModel


class AccountModel(BaseModel):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(Integer, default=1)
    status = Column(Integer, default=1)
    deleted_at = Column(DateTime)
    device_tokens = relationship("DeviceTokenModel", lazy=True, uselist=True)
    notify_users = relationship("NotifyUserModel", lazy=True, uselist=True)
    alert_setting = relationship("AlertSettingModel", lazy=True, uselist=False)

    # custom attributes
    badge: int = 0

    def is_enabled(self):
        return self.status == AccountStatus.ENABLE and not self.deleted_at

    def __repr__(self):
        return f"Account<id={self.id}>"
