import logging
from datetime import datetime

from openg2p_registry_bg_tasks_models.models import G2PQueBackgroundTask, TaskStatus
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from ..app import celery_app, get_engine
from ..config import Settings

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)
_engine = get_engine()


@celery_app.task(name="registry_beat_producer")
def registry_beat_producer():
    _logger.info("Checking for pending tasks")
    session_maker = sessionmaker(bind=_engine, expire_on_commit=False)

    with session_maker() as session:
        # Select entries that are PENDING and have not exceeded max attempts
        pending_request_entries = (
            session.execute(
                select(G2PQueBackgroundTask)
                .filter(
                    G2PQueBackgroundTask.task_status == TaskStatus.PENDING,
                )
                .limit(_config.batch_size)
            )
            .scalars()
            .all()
        )

        for entry in pending_request_entries:
            max_attempts = _config.worker_type_max_attempts.get(
                entry.worker_type, 3
            )
            if entry.number_of_attempts < max_attempts:
                entry.number_of_attempts += 1
                entry.last_attempt_datetime = datetime.utcnow()
                entry.queued_datetime = datetime.utcnow()
                _logger.info(f"Queueing task for id: {entry.id}")
                celery_app.send_task(
                    f"{entry.worker_type}",
                    args=(entry.id,),
                    queue=f"{entry.worker_type}",
                )
                session.commit()
    _logger.info("Completed checking for pending tasks")
