import logging
import os
import sys
import warnings

from dotenv import load_dotenv
from faker import Faker

warnings.filterwarnings(action="ignore", message=r"datetime.datetime.utcnow")  # noqa

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(BASE_DIR))
load_dotenv(os.path.join(BASE_DIR, ".env.local"))

logging.getLogger("faker").setLevel(logging.WARNING)
fake = Faker()

# fixtures ---------------------------------------------------------------------
