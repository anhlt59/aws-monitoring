import json
import os

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

with open(f"{CURRENT_DIR}/devices.json") as f:
    IMEIS = json.load(f)
