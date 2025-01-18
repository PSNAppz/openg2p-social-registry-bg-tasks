import enum
from datetime import datetime

from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import mapped_column


class TaskStatus(enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class G2PQueBackgroundTask(BaseORMModel):
    __tablename__ = "g2p_que_background_tasks"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_type = mapped_column(
        String, default="example_worker_task"
    )  # Default task type
    worker_payload = mapped_column(JSON, nullable=False)
    task_status = mapped_column(String, default=TaskStatus.PENDING)
    queued_datetime = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    number_of_attempts = mapped_column(Integer, default=0)
    last_attempt_datetime = mapped_column(DateTime, nullable=True)
    last_attempt_error_code = mapped_column(String, nullable=True)
