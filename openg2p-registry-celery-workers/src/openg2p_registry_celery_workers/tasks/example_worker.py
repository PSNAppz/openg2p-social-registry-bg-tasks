import logging
from datetime import datetime

from openg2p_registry_bg_tasks_models.models import G2PQueBackgroundTask, TaskStatus
from sqlalchemy.orm import sessionmaker

from ..app import celery_app, get_engine
from ..config import Settings

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)
_engine = get_engine()


@celery_app.task(name="example_worker")
def example_worker(id: int):
    _logger.info(f"Worker processing id: {id}")
    session_maker = sessionmaker(bind=_engine, expire_on_commit=False)
    with session_maker() as session:
        task_record = None
        try:
            task_record = session.query(G2PQueBackgroundTask).filter_by(id=id).first()
            if task_record:
                # Perform the main processing logic here...
                _logger.info(f"Worker Task Payload JSON: {task_record.worker_payload}")
                task_record.task_status = "COMPLETED"
                task_record.number_of_attempts += 1
                task_record.last_attempt_error_code = None
                task_record.last_attempt_datetime = datetime.utcnow()
                session.commit()
        except Exception as e:
            if task_record:
                task_record.task_status = TaskStatus.FAILED
                task_record.number_of_attempts += 1
                task_record.last_attempt_datetime = datetime.utcnow()
                task_record.last_attempt_error_code = str(e)
                session.commit()
            _logger.error(f"Worker task failed for id: {id}, error: {str(e)}")
