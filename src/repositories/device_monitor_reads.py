from src.models import DeviceMonitorReadModel

from .base import SqlRepository


class DeviceMonitorReadRepository(SqlRepository):
    model_class = DeviceMonitorReadModel
