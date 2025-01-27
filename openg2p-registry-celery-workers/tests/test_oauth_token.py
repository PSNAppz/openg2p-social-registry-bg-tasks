from datetime import datetime
from unittest.mock import MagicMock, patch

with patch(
    "src.openg2p_registry_celery_workers.config.Settings"
) as mock_settings, patch("logging.getLogger", return_value=MagicMock()), patch(
    "sqlalchemy.create_engine", return_value=MagicMock()
):
    mock_config = MagicMock()
    mock_config.auth_url = "http://auth.test.com"
    mock_config.auth_client_id = "TEST_CLIENT"
    mock_config.auth_client_secret = "TEST_SECRET"
    mock_config.auth_grant_type = "client_credentials"
    mock_settings.get_config.return_value = mock_config

    from src.openg2p_registry_celery_workers.helpers import OAuthTokenService


def test_get_oauth_token():
    service = OAuthTokenService()

    with patch(
        "src.openg2p_registry_celery_workers.helpers.oauth_token.OAuthTokenService.fetch_oauth_token",
        return_value="TEST_TOKEN",
    ):
        token = service.get_oauth_token()

    assert token == "TEST_TOKEN"


def test_fetch_oauth_token():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "access_token": "TEST_TOKEN",
        "expires_in": 3600,
    }

    mock_client = MagicMock()
    mock_client.post.return_value = mock_response

    with patch("httpx.Client") as mock_client_class:
        mock_client_class.return_value.__enter__.return_value = mock_client

        service = OAuthTokenService()
        token = service.fetch_oauth_token()

    assert token == "TEST_TOKEN"
    assert service.expiry > datetime.utcnow()
    mock_client.post.assert_called_once()
