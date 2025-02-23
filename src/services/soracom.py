import json
from functools import wraps
from typing import Iterable

import requests
from requests.exceptions import HTTPError

from src.base import SingletonMeta
from src.constants import SORACOM_AUTH_KEY_ID, SORACOM_AUTH_KEY_SECRET, SORACOM_ENDPOINT, SORACOM_REQUEST_TIMEOUT
from src.logger import logger


def auth_required():
    """Automatically authen when token is expired or not exist"""

    def decorated(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # call auth api if client.headers doesn't have X-Soracom-Token
            client: SoracomService = args[0]

            try:
                if not client.headers.get("X-Soracom-Token"):
                    client.auth()
                response = func(*args, **kwargs)
            except HTTPError as e:
                if 400 < e.response.status_code < 500:
                    logger.error(
                        f"SoracomClient.{func.__name__}: Got status {e.response.status_code} - {e.response.text}"
                    )
                    logger.warning(f"SoracomClient.{func.__name__}: retrying")
                    client.auth()
                    return func(*args, **kwargs)

                raise Exception(f"SORACOM_EXCEPTION - {e}")
            return response

        return wrapper

    return decorated


class SoracomService(metaclass=SingletonMeta):
    url = SORACOM_ENDPOINT
    timeout = SORACOM_REQUEST_TIMEOUT
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def auth(
        self, auth_key: str = SORACOM_AUTH_KEY_SECRET, auth_key_id: str = SORACOM_AUTH_KEY_ID, timeout: int = timeout
    ):
        # https://developers.soracom.io/en/api/#!/Auth/auth
        payload = {
            "authKey": auth_key,
            "authKeyId": auth_key_id,
            "tokenTimeoutSeconds": 86400,
        }
        response = requests.post(f"{self.url}/auth", headers=self.headers, data=json.dumps(payload), timeout=timeout)
        response.raise_for_status()
        data = response.json()
        self.headers.update({"X-Soracom-Api-Key": data["apiKey"], "X-Soracom-Token": data["token"]})

    @auth_required()
    def add_subscription(self, sim_id: str, body: dict, timeout: int = timeout):
        # https://developers.soracom.io/en/api/#!/Sim/addSubscription
        logger.debug(f"Soracom.add_subscription: sim_id={sim_id}, body={body}")
        response = requests.post(
            f"{self.url}/sims/{sim_id}/profiles/{sim_id}/add_subscription",
            headers=self.headers,
            data=json.dumps(body),
            timeout=timeout,
        )
        if response.status_code == 200:
            logger.debug(f"Request to update SIM plan successfully: {response.json()}")
        elif response.status_code == 400:
            logger.error(f"Failed to update SIM plan: {response.json()}")
        elif response.status_code == 404:
            logger.error(f"SIM#{sim_id} not found: {response.json()}")
        else:
            logger.error(f"Unknown error: {response.text}")
        response.raise_for_status()
        return response.json()

    @auth_required()
    def search_sims(
        self,
        sim_ids: Iterable[str] | None = None,
        session_status: str = "NA",
        search_type: str = "and",
        limit: int = 100,
        timeout: int = timeout,
    ) -> list:
        # https://developers.soracom.io/en/api/#!/Query/searchSims
        logger.debug(f"Soracom.search_sims: sim_id={sim_ids}")
        params = {"session_status": session_status, "search_type": search_type, "limit": limit}
        if sim_ids:
            params["sim_id"] = ",".join(sim_ids)

        response = requests.get(f"{self.url}/query/sims", headers=self.headers, params=params, timeout=timeout)
        response.raise_for_status()
        logger.debug(f"Soracom.search_sims: got {len(response.json())} sims")
        return response.json()
