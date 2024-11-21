import logging
from datetime import datetime

from openg2p_sr_models.models import G2PQueIDGeneration, IDGenerationRequestStatus
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from ..app import celery_app, get_engine
from ..config import Settings

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)
_engine = get_engine()


@celery_app.task(name="id_generation_request_beat_producer")
def id_generation_request_beat_producer():
    _logger.info("Checking for registrants pending ID generation request")
    session_maker = sessionmaker(bind=_engine, expire_on_commit=False)

    with session_maker() as session:
        # Update entries that have exceeded max attempts to FAILED for request status
        session.query(G2PQueIDGeneration).filter(
            G2PQueIDGeneration.id_generation_request_status
            == IDGenerationRequestStatus.PENDING,
            G2PQueIDGeneration.number_of_attempts_request
            >= _config.max_id_generation_request_attempts,
        ).update(
            {
                G2PQueIDGeneration.id_generation_request_status: IDGenerationRequestStatus.FAILED,
                G2PQueIDGeneration.last_attempt_datetime_request: datetime.utcnow(),
            },
            synchronize_session=False,
        )
        session.commit()

        # Select entries that are PENDING for request status and have not exceeded max attempts
        pending_request_entries = (
            session.execute(
                select(G2PQueIDGeneration).filter(
                    G2PQueIDGeneration.id_generation_request_status
                    == IDGenerationRequestStatus.PENDING,
                    G2PQueIDGeneration.number_of_attempts_request
                    < _config.max_id_generation_request_attempts,
                )
            )
            .scalars()
            .all()
        )

        for entry in pending_request_entries:
            registrant_id = entry.registrant_id
            _logger.info(
                f"Queueing ID generation request task for registrant_id: {registrant_id}"
            )
            celery_app.send_task(
                "id_generation_request_worker",
                args=(registrant_id,),
                queue="social_registry_queue",
            )

    _logger.info("Completed checking for registrants pending ID generation request")
