import json
from datetime import date, datetime

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import attributes, declarative_base

from src.constants import DATETIME_FORMAT

Base = declarative_base()


class BaseModel(Base):
    __slots__ = ()
    __abstract__ = True

    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        onupdate=datetime.utcnow,
        default=datetime.utcnow,
        server_default=func.current_timestamp(),
    )

    @staticmethod
    def _json_serializer(_obj):
        if isinstance(_obj, datetime) or isinstance(_obj, date):
            return _obj.strftime(DATETIME_FORMAT)

    def to_dict(self, ignore_null=True) -> dict:
        if ignore_null is False:
            return {column.name: getattr(self, column.name) for column in self.__table__.columns}

        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns if getattr(self, column.name)
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=self._json_serializer)

    def to_log(self) -> str:
        item = dict(
            (column.name, getattr(self, column.name))
            for column in self.__table__.columns
            if getattr(self, column.name)
        )
        return json.dumps(item, default=self._json_serializer)

    @classmethod
    def deserialize(cls, data: dict):
        # deserialize
        for column in cls.__table__.columns:
            if isinstance(column.type, DateTime):
                if value := data.get(column.name):
                    data[column.name] = datetime.strptime(value, DATETIME_FORMAT)
        return cls(**data)

    def is_modified(self):
        return attributes.instance_state(self).modified
