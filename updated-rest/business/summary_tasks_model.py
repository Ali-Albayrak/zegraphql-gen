import os
from core.logger import log
from core.custom_exceptions import TriggerException




import enum
from sqlalchemy import DATETIME, String, ForeignKey
from sqlalchemy import Enum, ARRAY, DATE, Column, Text
from sqlalchemy.orm import relationship
from core.base_model import BaseModel
from core.manager import Manager
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select



# select enums
class StatusEnum(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class Summary_TaskModel(BaseModel):
    __tablename__ = 'summary_tasks'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}


    status = Column(Enum(StatusEnum), nullable=False, default=None)

    questions = Column(ARRAY(Text), nullable=False, default=None)

    min_max = Column(Text, nullable=False, default=None)

    word_count = Column(Text, nullable=False, default=None)

    source = Column(Text, nullable=True, default=None)

    industry = Column(ARRAY(Text), nullable=True, default=None)

    category = Column(ARRAY(Text), nullable=False, default=None)

    tags = Column(ARRAY(Text), nullable=True, default=None)

    release_date = Column(DATE, nullable=True, default=None)

    expiry_date = Column(DATE, nullable=True, default=None)

    html = Column(Text, nullable=True, default=None)

    pdf = Column(UUID(as_uuid=True), ForeignKey("public.files.id"))

    name = Column(Text, nullable=True, default=None)

    @classmethod
    async def objects(cls, session):
        obj = await Manager.async_init(cls, session)
        return obj



