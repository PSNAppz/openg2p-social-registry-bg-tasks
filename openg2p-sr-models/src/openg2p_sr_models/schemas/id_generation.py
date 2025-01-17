from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class IDGenerationStatusEnum(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class G2PQueIDGenerationModel(BaseModel):
    id: Optional[int]
    registrant_id: str
    id_generation_status: IDGenerationStatusEnum
    queued_datetime: datetime
    number_of_attempts: int
    last_attempt_datetime: Optional[datetime]
    last_attempt_error_code: Optional[str]


class ResPartnerModel(BaseModel):
    registrant_id: int
    unique_id: Optional[str]
