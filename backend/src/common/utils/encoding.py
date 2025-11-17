import base64
import json


def json_to_base64(value: dict | str) -> str:
    json_bytes = json.dumps(value).encode("utf-8")
    base64_bytes = base64.b64encode(json_bytes)
    return base64_bytes.decode("utf-8")


def base64_to_json(value: str) -> dict:
    base64_bytes = value.encode("utf-8")
    json_bytes = base64.b64decode(base64_bytes)
    return json.loads(json_bytes.decode("utf-8"))
