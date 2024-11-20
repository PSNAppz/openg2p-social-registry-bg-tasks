import logging
from datetime import datetime, timedelta

import httpx
from openg2p_fastapi_common.service import BaseService

from ..config import Settings

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)


class OAuthTokenService(BaseService):
    def __init__(self):
        super().__init__()
        self.oauth_token = None
        self.expiry = datetime.utcnow()

    def get_oauth_token(self):
        if self.oauth_token is None or datetime.utcnow() >= self.expiry:
            self.oauth_token = self.fetch_oauth_token()
        return self.oauth_token

    def fetch_oauth_token(self):
        url = _config.auth_url
        payload = {
            "client_id": _config.auth_client_id,
            "client_secret": _config.auth_client_secret,
            "grant_type": _config.auth_grant_type,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        with httpx.Client() as client:
            response = client.post(url, data=payload, headers=headers)
            response_data = response.json()
            expires_in = response_data.get("expires_in", 900)
            self.expiry = datetime.utcnow() + timedelta(seconds=expires_in)
            return response_data["access_token"]
