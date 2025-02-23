import json

from sqlalchemy import Column, ForeignKey, Integer, String

from .base import BaseModel


class DeviceTokenModel(BaseModel):
    __tablename__ = "device_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), index=True)
    device_token = Column(String(200))
    is_login = Column(Integer, default=1)

    def to_json(self) -> str:
        item = {
            "id": self.id,
            "account_id": self.account_id,
            "device_token": f"{(self.device_token or ''):.20}",
            "is_login": self.is_login,
        }
        return json.dumps(item)

    def __repr__(self):
        return f"DeviceToken<id={self.id}, account_id={self.account_id}>"
