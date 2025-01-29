from unittest.mock import MagicMock

import pytest
from openg2p_registry_bg_tasks_models.models import G2PQueBackgroundTask, TaskStatus
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session(mocker):
    session = MagicMock(spec=Session)
    session_maker = MagicMock()
    session_maker.return_value.__enter__.return_value = session

    mocker.patch("sqlalchemy.orm.sessionmaker", return_value=session_maker)
    return session


@pytest.fixture
def mock_celery_send_task(mocker):
    return mocker.patch(
        "openg2p_registry_celery_beat_producers.app.celery_app.send_task"
    )


def test_registry_beat_producer(mock_session, mock_celery_send_task):
    from openg2p_registry_celery_beat_producers.tasks.registry_beat_producer import (
        registry_beat_producer,
    )

    test_task = G2PQueBackgroundTask(
        id=1,
        worker_type="test_worker",
        task_status=TaskStatus.PENDING,
        number_of_attempts=0,
        last_attempt_datetime=None,
        queued_datetime=None,
    )

    mock_session.execute.return_value.scalars.return_value.all.return_value = [
        test_task
    ]

    registry_beat_producer()

    mock_session.commit.assert_called_once()
    mock_celery_send_task.assert_called_once()
    assert test_task.number_of_attempts == 1
