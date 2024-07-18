import enum
import datetime
from typing import Optional, TYPE_CHECKING
import strawberry
from strawberry.permission import PermissionExtension

from .base import BaseType
from core.auth import Protect

# select enums
@strawberry.enum
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

@strawberry.enum
class StatusEnum(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"
    update = "update"
    delete = "delete"
@strawberry.input
class CreateDocumentInput(BaseType):
    id: Optional[strawberry.ID] = None
    name: str
    report_source: str
    release_date: Optional[datetime.date]
    expiry_date: Optional[datetime.date]
    industry_document: Optional[strawberry.ID]
    category: Optional[CategoryEnum]
    tags: Optional[str]
    original_pdf: Optional[strawberry.ID]
    status: Optional[CategoryEnum]

@strawberry.input
class UpdateDocumentInput(BaseType):
    id: Optional[strawberry.ID] = None
    name: Optional[str] = None
    report_source: Optional[str] = None
    release_date: Optional[datetime.date] = None
    expiry_date: Optional[datetime.date] = None
    industry_document: Optional[strawberry.ID] = None
    category: Optional[CategoryEnum] = None
    tags: Optional[str] = None
    original_pdf: Optional[strawberry.ID] = None
    status: Optional[CategoryEnum] = None
