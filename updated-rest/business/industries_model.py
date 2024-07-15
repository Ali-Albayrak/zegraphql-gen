import os
from core.logger import log
from core.custom_exceptions import TriggerException
import importlib




import enum
from sqlalchemy import DATETIME, String, ForeignKey
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.base_model import BaseModel
from core.manager import Manager
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select



# select enums


class IndustryModel(BaseModel):
    __tablename__ = 'industries'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}


    from business.documents_model import DocumentModel
    industry_document = relationship('DocumentModel', foreign_keys=[DocumentModel.industry_document], back_populates='industry_document__details')

    industry_name = Column(Text, nullable=True, default=None)

    @classmethod
    async def objects(cls, session):
        obj = await Manager.async_init(cls, session)
        return obj



