from datetime import datetime, timedelta
from typing import Iterable

from sqlalchemy import and_, case, desc, func

from src.models import StatisticModel

from .base import SqlExtendedRepository, transaction


class StatisticRepository(SqlExtendedRepository):
    model_class = StatisticModel

    def group_statistics_by_imei(
        self, imeis: Iterable[str], since: datetime, until: datetime
    ) -> dict[str:StatisticModel]:
        # list all statistics matching imeis, since, until
        results = self.query.filter(
            and_(
                StatisticModel.imei.in_(imeis),
                StatisticModel.sensor_time >= since,
                StatisticModel.sensor_time <= until,
            )
        ).all()

        # group the results by imei
        statistics: dict[str, list[StatisticModel]] = {}
        for item in results:
            if values := statistics.get(item.imei):
                values.append(item)
            else:
                statistics[item.imei] = [item]
        return statistics

    def get_last_statistic(self, imei: str | None = None) -> StatisticModel:
        query = self.query.filter(StatisticModel.imei == imei) if imei else self.query
        return query.order_by(desc(StatisticModel.id)).first()

    def count_co2_diff_below_threshold(
        self, imeis: list[str], since: datetime, until: datetime, threshold: int = 35
    ) -> Iterable[tuple[str, int, int]]:
        """
        :return: [(imei, match, total, ...]
        """
        exceeding_case = case((and_(func.abs(StatisticModel.co2_diff) < threshold), 1), else_=None)
        return (
            self.session.query(
                StatisticModel.imei,
                func.count(exceeding_case).label("match"),
                func.count().label("total"),
            )
            .filter(
                and_(
                    StatisticModel.imei.in_(imeis),
                    StatisticModel.sensor_time >= since,
                    StatisticModel.sensor_time <= until,
                    StatisticModel.co2_diff.isnot(None),
                )
            )
            .group_by(StatisticModel.imei)
            .all()
        )

    @transaction
    def delete_expired_statistics(self, expired_days=7):
        expired_datetime = datetime.utcnow().date() - timedelta(days=expired_days)
        self.query.filter(StatisticModel.sensor_time <= expired_datetime).delete()
