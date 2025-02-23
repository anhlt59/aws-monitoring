from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from .base import BaseModel


class NotifyUserModel(BaseModel):
    __tablename__ = "notify_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), index=True)
    notify_user_email = Column(String(100))
    notify_user_name = Column(String(100))
    deleted_at = Column(DateTime)

    def __repr__(self):
        return f"NotifyUser<id={self.id}, account_id={self.account_id}>"
