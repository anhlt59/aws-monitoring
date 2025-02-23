from src.models import DeviceTokenModel

from .base import SqlRepository


class DeviceTokenRepository(SqlRepository):
    model_class = DeviceTokenModel
