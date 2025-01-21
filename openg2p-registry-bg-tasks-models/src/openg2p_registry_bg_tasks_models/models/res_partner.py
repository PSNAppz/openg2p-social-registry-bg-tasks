from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column


class ResPartner(BaseORMModel):
    __tablename__ = "res_partner"

    id = mapped_column(Integer, primary_key=True)
    unique_id = mapped_column(String)
