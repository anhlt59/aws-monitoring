from sqlalchemy import Column, DateTime, Float, Index, Integer, String

from .base import BaseModel


class StatisticModel(BaseModel):
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    imei = Column(String(20))
    sensor_time = Column(DateTime, index=True)
    co2 = Column(Integer)
    temp = Column(Float)
    humid = Column(Integer)
    # the different between the current co2 and the co2 from 25 minutes ago
    co2_diff = Column(Integer, default=None, nullable=True)

    __table_args__ = (Index("imei_sensortime_idx", "imei", "sensor_time"),)

    def __repr__(self):
        return f"Statistic<id={self.id}, imei={self.imei}>"
