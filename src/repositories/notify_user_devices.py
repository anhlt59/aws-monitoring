from src.models import NotifyUserDeviceModel

from .base import SqlRepository


class NotifyUserDeviceRepository(SqlRepository):
    model_class = NotifyUserDeviceModel
