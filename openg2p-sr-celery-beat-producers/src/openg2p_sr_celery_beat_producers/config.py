from openg2p_fastapi_common.config import Settings as BaseSettings
from pydantic_settings import SettingsConfigDict

from . import __version__


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="sr_celery_beat_", env_file=".env", extra="allow"
    )
    openapi_title: str = "OpenG2P SR Celery Tasks"
    openapi_description: str = """
        Celery tasks for OpenG2P Social Registry
        ***********************************
        Further details goes here
        ***********************************
        """
    openapi_version: str = __version__

    db_dbname: str = "socialregistrydb"
    db_driver: str = "postgresql"

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_backend_url: str = "redis://localhost:6379/0"

    max_id_generation_request_attempts: int = 3
    max_id_generation_update_attempts: int = 3

    res_partner_id_generation_frequency: int = 10
    res_partner_id_update_frequency: int = 10

    batch_size: int = 10000
