# ruff: noqa: E402

from .config import Settings

_config = Settings.get_config()

from celery import Celery
from openg2p_fastapi_common.app import Initializer as BaseInitializer
from openg2p_fastapi_common.exception import BaseExceptionHandler

from sqlalchemy import create_engine


class Initializer(BaseInitializer):
    def initialize(self, **kwargs):
        super().init_logger()
        super().init_app()
        BaseExceptionHandler()



def get_engine():
    if _config.db_datasource:
        db_engine = create_engine(_config.db_datasource)
        return db_engine


celery_app = Celery(
    "g2p_sr_celery_beat_producer",
    broker=_config.celery_broker_url,
    backend=_config.celery_backend_url,
    include=["openg2p_sr_celery_beat_producers.tasks"],
)

celery_app.conf.beat_schedule = {
    "id_generation_request_beat_producer": {
        "task": "id_generation_request_beat_producer",
        "schedule": _config.res_partner_id_generation_frequency,
    },
    "id_generation_update_beat_producer": {
        "task": "id_generation_update_beat_producer",
        "schedule": _config.res_partner_id_update_frequency,
    },
}
celery_app.conf.timezone = "UTC"
