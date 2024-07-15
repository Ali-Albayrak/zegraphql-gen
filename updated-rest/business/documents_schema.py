
from typing import Optional, Union
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr, Field
from core.encrypt_str import EncryptStr



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
# select enums
class StatusEnum(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"
    update = "update"
    delete = "delete"


class CreateDocument(BaseModel):
    id: Optional[uuid.UUID]
    name: str
    report_source: str
    release_date: datetime.date
    expiry_date: Optional[datetime.date] = Field(default=None)
    industry_document: Optional[uuid.UUID] = Field(default=None)
    category: CategoryEnum
    tags: Optional[str] = Field(default=None)
    original_pdf: uuid.UUID
    status: Optional[StatusEnum] = Field(default=None)

    @validator('industry_document')
    def validate_industry_document(cls, industry_document: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <industry_document> is not allowed")
        return industry_document
    @validator('category')
    def validate_category(cls, category: CategoryEnum):
        if False or False or False:
            raise ValueError(f"field <category> is not allowed")
        return category
    @validator('status')
    def validate_status(cls, status: Optional[StatusEnum] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <status> is not allowed")
        return status

class ReadDocument(BaseModel):
    id: uuid.UUID
    created_on: datetime.datetime
    updated_on: datetime.datetime
    created_by: Optional[uuid.UUID] = Field(default=None)
    updated_by: Optional[uuid.UUID] = Field(default=None)
    tenant_id: Optional[uuid.UUID] = Field(default=None)
    name: str
    report_source: str
    release_date: datetime.date
    expiry_date: Optional[datetime.date] = Field(default=None)
    industry_document: Optional[uuid.UUID] = Field(default=None)
    industry_document__details: Optional[object] = Field(default={})
    category: CategoryEnum
    tags: Optional[str] = Field(default=None)
    original_pdf: uuid.UUID
    status: Optional[StatusEnum] = Field(default=None)


    @validator('category')
    def validate_category(cls, category: CategoryEnum):
        return category

    @validator('status')
    def validate_status(cls, status: Optional[StatusEnum] = Field(default=None)):
        return status

    class Config:
        orm_mode = True


class UpdateDocument(BaseModel):
    name: Optional[str] = Field(default=None)
    report_source: Optional[str] = Field(default=None)
    release_date: Optional[datetime.date] = Field(default=None)
    expiry_date: Optional[datetime.date] = Field(default=None)
    industry_document: Optional[uuid.UUID] = Field(default=None)
    category: Optional[CategoryEnum] = Field(default=None)
    tags: Optional[str] = Field(default=None)
    original_pdf: Optional[uuid.UUID] = Field(default=None)
    status: Optional[StatusEnum] = Field(default=None)


    @validator('category')
    def validate_category(cls, category: CategoryEnum):
        if False or '__' in category or category in ['id']:
            raise ValueError(f"field <category> is not allowed")
        return category

    @validator('status')
    def validate_status(cls, status: Optional[StatusEnum] = Field(default=None)):
        if False or '__' in status or status in ['id']:
            raise ValueError(f"field <status> is not allowed")
        return status

    class Config:
        orm_mode = True


class ReadDocuments(BaseModel):
    data: list[Optional[ReadDocument]]
    next_page: Union[str, int]
    page_size: int




class DocumentsAccess:
    related_access_roles = ['cybernetic-karari-documents-list', 'cybernetic-karari-documents-tenant-list', 'cybernetic-karari-documents-root-list', 'cybernetic-karari-industries-list', 'cybernetic-karari-industries-tenant-list', 'cybernetic-karari-industries-root-list']

    @classmethod
    def list_roles(cls):
        list_roles = ['cybernetic-karari-documents-list', 'cybernetic-karari-documents-tenant-list', 'cybernetic-karari-documents-root-list']
        return list(set(list_roles + cls.related_access_roles))

    @classmethod
    def create_roles(cls):
        create_roles = ['cybernetic-karari-documents-create', 'cybernetic-karari-documents-tenant-create', 'cybernetic-karari-documents-root-create']
        return create_roles + cls.related_access_roles

    @classmethod
    def update_roles(cls):
        update_roles = ['cybernetic-karari-documents-update', 'cybernetic-karari-documents-tenant-update', 'cybernetic-karari-documents-root-update']
        return update_roles + cls.related_access_roles

    @classmethod
    def delete_roles(cls):
        delete_roles = ['cybernetic-karari-documents-delete', 'cybernetic-karari-documents-tenant-delete', 'cybernetic-karari-documents-root-delete']
        return delete_roles + cls.related_access_roles