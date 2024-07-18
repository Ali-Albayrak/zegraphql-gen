from typing import Optional
import datetime
import strawberry
from strawberry.permission import PermissionExtension

from .base import BaseType
from core.auth import Protect

@strawberry.type
class DocumentType(BaseType):
    id: strawberry.ID 
    created_on: Optional[datetime.datetime]
    updated_on: Optional[datetime.datetime]
    created_by: Optional[strawberry.ID]
    updated_by: Optional[strawberry.ID]
    tenant_id: Optional[strawberry.ID]
    name: Optional[str]
    report_source: Optional[str]
    release_date: Optional[datetime.date]
    expiry_date: Optional[datetime.date]
    industry_document: Optional[strawberry.ID]
    industry_document__details: Optional["IndustryType"]
    category: Optional[str]
    tags: Optional[str]
    original_pdf: Optional[strawberry.ID]
    status: Optional[str]

@strawberry.type
class IndustryType(BaseType):
    id: strawberry.ID
    created_on: datetime.datetime
    updated_on: datetime.datetime
    created_by: Optional[strawberry.ID]
    updated_by: Optional[strawberry.ID]
    tenant_id: Optional[strawberry.ID]
    industry_document: Optional[list["DocumentType"]] 
    industry_name: Optional[str]
