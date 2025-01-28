from unittest.mock import MagicMock, patch

import pytest
from openg2p_registry_bg_tasks_models.models import (
    G2PQueBackgroundTask,
    ResPartner,
    TaskStatus,
)
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session():
    session = MagicMock(spec=Session)
    session_maker = MagicMock()
    session_maker.return_value.__enter__.return_value = session

    with patch("sqlalchemy.orm.sessionmaker", return_value=session_maker):
        yield session


@pytest.fixture
def mock_response():
    response = MagicMock()

    with patch("httpx.put", return_value=response):
        yield response


@patch("openg2p_registry_celery_workers.helpers.OAuthTokenService.get_component")
def test_id_generation_update_worker_success(
    mock_oauth_service, mock_session, mock_response
):
    # Importing target function within the patch scope
    from openg2p_registry_celery_workers.tasks.id_generation_update_worker import (
        id_generation_update_worker,
    )

    mock_oauth_service.get_oauth_token.return_value = "TEST_TOKEN"
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": {"uin": "TEST_UIN"},
        "test": "response",
    }
    mock_fetch = [
        G2PQueBackgroundTask(
            id=1,
            worker_type="TEST_WORKER",
            worker_payload={"registrant_id": 1},
            task_status=TaskStatus.PENDING,
            number_of_attempts=0,
        ),
        ResPartner(id=1, unique_id="TEST_UID_1"),
    ]
    mock_session.query.return_value.filter.return_value.first.side_effect = mock_fetch

    id_generation_update_worker(1)

    assert mock_fetch[0].number_of_attempts == 1
    mock_session.commit.assert_called()
