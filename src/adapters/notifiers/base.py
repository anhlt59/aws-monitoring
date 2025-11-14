import json
from typing import Any

import aiohttp
from pydantic import BaseModel

from src.common.utils.template import render_template


class Message(BaseModel):
    body: str | None = None
    attachments: list[Any] | None = None


class SlackClient:
    def __init__(self, webhook_url: str, timeout: int = 10):
        self.webhook_url = webhook_url
        self.timeout = timeout

    async def send(self, message: Message):
        headers = {"Content-Type": "application/json"}
        payload = {
            "text": message.body or "",
            "attachments": message.attachments if message.attachments else [],
        }
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(self.webhook_url, headers=headers, json=payload) as response:
                response.raise_for_status()


def render_message(template_file: str, context: dict | None = None) -> Message:
    """Load message template from a file."""
    try:
        json_data = render_template(template_file, context or {})
        data = json.loads(json_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from template '{template_file}': {e}")
    except Exception as e:
        raise ValueError(f"Failed to render template '{template_file}': {e}")

    return Message(body=data.get("body"), attachments=data.get("attachments", []))
