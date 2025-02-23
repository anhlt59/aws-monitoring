from sqlalchemy.orm import close_all_sessions

from src.logger import logger
from src.repositories import StatisticRepository

EXPIRED_DAYS = 7
statistic_repository = StatisticRepository()


def handler(event, context):
    try:
        statistic_repository.delete_expired_statistics(EXPIRED_DAYS)
        logger.debug("Deleted expired statistics")
    except Exception as e:
        logger.error(f"`delete_statistics` failed: {e}")
    close_all_sessions()
