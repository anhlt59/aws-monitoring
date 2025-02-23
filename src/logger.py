import logging
import sys
import traceback

from src.constants import LOG_FORMAT, LOG_LEVEL, STAGE


class TracebackHandler(logging.StreamHandler):
    def emit(self, record):
        # ERROR levelno = 40
        if STAGE != "prod" and record.levelno >= 40:
            exc_type, *_ = sys.exc_info()
            if exc_type:
                record.msg = f"TRACEBACK - {record.msg} - {traceback.format_exc().splitlines()}"
        super().emit(record)


logger = logging.getLogger()

for h in logger.handlers:
    logger.removeHandler(h)
handler = TracebackHandler(sys.stdout)
handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(handler)

# set log level
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("pynamodb").setLevel(logging.WARNING)
