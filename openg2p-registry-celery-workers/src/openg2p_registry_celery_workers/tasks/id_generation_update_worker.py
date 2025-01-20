import logging
from datetime import datetime

import httpx
from openg2p_registry_bg_tasks_models.models import (
    G2PQueBackgroundTask,
    ResPartner,
    TaskStatus,
)
from sqlalchemy.orm import sessionmaker

from ..app import celery_app, get_engine
from ..config import Settings
from ..helpers import OAuthTokenService

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)
_engine = get_engine()


@celery_app.task(name="id_generation_update_worker")
def id_generation_update_worker(id: int):
    _logger.info("Starting ID generation update")
    session_maker = sessionmaker(bind=_engine, expire_on_commit=False)

    with session_maker() as session:
        queue_entry = None
        try:
            # Fetch the queue entry
            queue_entry = (
                session.query(G2PQueBackgroundTask)
                .filter(G2PQueBackgroundTask.id == id)
                .first()
            )

            if not queue_entry:
                _logger.error(f"No queue entry found for task_id: {id}")
                return
            registrant_id = queue_entry.worker_payload.get("registrant_id")
            # Fetch res_partner to get the UIN
            res_partner = (
                session.query(ResPartner).filter(ResPartner.id == registrant_id).first()
            )

            if not res_partner or not res_partner.unique_id:
                raise Exception(
                    f"No UIN found for registrant_id: {registrant_id} in res_partner"
                )

            # Get OIDC token
            access_token = OAuthTokenService.get_component().get_oauth_token()
            _logger.info("Received access token")

            if not access_token:
                raise Exception("Failed to retrieve access token from token response")

            headers = {
                "Cookie": f"Authorization={access_token}",
                "Accept": "application/json",
            }
            current_datetime = datetime.utcnow()
            formatted_datetime = (
                current_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            )

            # Call MOSIP Update UIN API to update status
            update_payload = {
                "id": "string",
                "metadata": {},
                "request": {"uin": res_partner.unique_id, "status": "ASSIGNED"},
                "requesttime": formatted_datetime,
                "version": "string",
            }
            response = httpx.put(
                _config.mosip_update_uin_url, json=update_payload, headers=headers
            )
            _logger.info(
                f"Received response from MOSIP Update UIN API: {response.text}"
            )
            if response.status_code != 200:
                raise Exception(
                    f"MOSIP Update UIN API call failed with status code {response.status_code}"
                )

            # Status code is 200
            if response.json().get("errors"):
                raise Exception(
                    f"MOSIP Update UIN API call failed with error: {response.json().get('errors')}"
                )

            # Status is 200 and No errors then update queue entry statuses
            queue_entry.number_of_attempts += 1
            queue_entry.task_status = TaskStatus.COMPLETED
            queue_entry.last_attempt_datetime = datetime.utcnow()
            queue_entry.last_attempt_error_code = None
            session.commit()

            _logger.info(f"Mosip update completed for registrant_id: {registrant_id}")

        except Exception as e:
            error_message = f"Error during ID generation update for registrant_id {registrant_id}: {str(e)}"
            _logger.error(error_message)

            if queue_entry:
                queue_entry.number_of_attempts += 1
                queue_entry.last_attempt_datetime = datetime.utcnow()
                queue_entry.last_attempt_error_code = str(e)
                if (
                    queue_entry.number_of_attempts
                    >= _config.worker_type_max_attempts.get(
                        "max_id_generation_update_attempts"
                    )
                ):
                    queue_entry.task_status = TaskStatus.FAILED
                session.commit()
        _logger.info(
            f"Completed ID generation update for registrant_id: {registrant_id}"
        )
