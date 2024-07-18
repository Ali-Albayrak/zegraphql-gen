import os
from datetime import datetime
from core.logger import log
from core.custom_exceptions import TriggerException
import importlib




import enum
from sqlalchemy import DATETIME, String, ForeignKey
from sqlalchemy import Enum, String, ForeignKey, DATE, Column, Text
from sqlalchemy.orm import relationship
from core.base_model import BaseModel
from core.manager import Manager
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select



# select enums
class CategoryEnum(str, enum.Enum):
    hr = "hr"
    it = "it"
    marketing = "marketing"
    market_research = "market_research"
    finance = "finance"
    sales = "sales"
    startegy = "startegy"
    plan = "plan"
    operations = "operations"
    research_development = "research_development"
    product_management = "product_management"
    service_management = "service_management"
    customer_service = "customer_service"
    risk_management = "risk_management"
    audit = "audit"
    investment = "investment"
class StatusEnum(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"
    update = "update"
    delete = "delete"

from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, func, select, DATE
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class DocumentModel(BaseModel):
    __tablename__ = 'documents'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}

    name: Mapped[str] = mapped_column(nullable=False, default=None)
    report_source: Mapped[str] = mapped_column(nullable=False, default=None)
    release_date: Mapped[datetime] = mapped_column(nullable=False, default=None)
    expiry_date: Mapped[datetime] = mapped_column(nullable=True, default=None)
    industry_document: Mapped[UUID] = mapped_column(ForeignKey(os.environ.get('DEFAULT_SCHEMA', 'public') + ".industries.id"))
    industry_document__details: Mapped["IndustryModel"] = relationship(foreign_keys=[industry_document], back_populates='industry_document', lazy='selectin')
    category: Mapped[CategoryEnum] = mapped_column(nullable=False, default=None)
    tags: Mapped[str] = mapped_column(nullable=True, default=None)
    original_pdf: Mapped[UUID] = mapped_column(ForeignKey("public.files.id"))
    status: Mapped[StatusEnum] = mapped_column(nullable=True, default=None)

    @classmethod
    def objects(cls, session):
        return Manager(cls, session)



