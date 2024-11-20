import logging
from datetime import datetime

from openg2p_sr_models.models import G2PQueIDGeneration, IDGenerationRequestStatus, IDGenerationUpdateStatus
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from ..app import celery_app, get_engine
from ..config import Settings

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)
_engine = get_engine()


@celery_app.task(name="id_generation_update_beat_producer")
def id_generation_update_beat_producer():
    _logger.info("Checking for registrants pending ID generation update")
    session_maker = sessionmaker(bind=_engine, expire_on_commit=False)

    with session_maker() as session:
        # Update entries that have exceeded max attempts to FAILED for update status
        session.query(G2PQueIDGeneration).filter(
            G2PQueIDGeneration.id_generation_update_status
            == IDGenerationUpdateStatus.PENDING,
            G2PQueIDGeneration.number_of_attempts_update >= _config.max_id_generation_update_attempts,
        ).update(
            {
                G2PQueIDGeneration.id_generation_update_status: IDGenerationUpdateStatus.FAILED,
                G2PQueIDGeneration.last_attempt_datetime: datetime.utcnow(),
            },
            synchronize_session=False,
        )
        session.commit()

        # Select entries that have COMPLETED request and PENDING update status
        pending_update_entries = (
            session.execute(
                select(G2PQueIDGeneration).filter(
                    G2PQueIDGeneration.id_generation_request_status
                    == IDGenerationRequestStatus.COMPLETED,
                    G2PQueIDGeneration.id_generation_update_status
                    == IDGenerationUpdateStatus.PENDING,
                    G2PQueIDGeneration.number_of_attempts_update
                    < _config.max_id_generation_update_attempts,
                )
            )
            .scalars()
            .all()
        )

        for entry in pending_update_entries:
            registrant_id = entry.registrant_id
            _logger.info(
                f"Queueing ID generation update task for registrant_id: {registrant_id}"
            )
            celery_app.send_task(
                "id_generation_update_worker",
                args=(registrant_id,),
                queue="social_registry_queue",
            )

    _logger.info("Completed checking for registrants pending ID generation update")