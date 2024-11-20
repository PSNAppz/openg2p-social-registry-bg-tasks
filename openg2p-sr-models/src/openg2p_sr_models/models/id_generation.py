import enum
from datetime import datetime

from openg2p_fastapi_common.models import BaseORMModel, BaseORMModelWithTimes
from sqlalchemy import DateTime, Integer, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import mapped_column


class IDGenerationRequestStatus(enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class IDGenerationUpdateStatus(enum.Enum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class G2PQueIDGeneration(BaseORMModelWithTimes):
    __tablename__ = "g2p_que_id_generation"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    registrant_id = mapped_column(String, nullable=False, unique=True)
    id_generation_request_status = mapped_column(
        SqlEnum(IDGenerationRequestStatus),
        nullable=False,
        default=IDGenerationRequestStatus.PENDING,
    )
    id_generation_update_status = mapped_column(
        SqlEnum(IDGenerationUpdateStatus),
        nullable=False,
        default=IDGenerationUpdateStatus.NOT_APPLICABLE,
    )
    queued_datetime = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    number_of_attempts_request = mapped_column(Integer, nullable=False, default=0)
    number_of_attempts_update = mapped_column(Integer, nullable=False, default=0)
    last_attempt_error_code_request = mapped_column(String)
    last_attempt_error_code_update = mapped_column(String)
    last_attempt_datetime = mapped_column(DateTime)


class ResPartner(BaseORMModel):
    __tablename__ = "res_partner"

    registrant_id = mapped_column(String, primary_key=True)
    ref_id = mapped_column(String)
