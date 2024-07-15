
from typing import Optional, Union
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr, Field
from core.encrypt_str import EncryptStr





class CreateIndustry(BaseModel):
    id: Optional[uuid.UUID]
    industry_name: Optional[str] = Field(default=None)


class ReadIndustry(BaseModel):
    id: uuid.UUID
    created_on: datetime.datetime
    updated_on: datetime.datetime
    created_by: Optional[uuid.UUID] = Field(default=None)
    updated_by: Optional[uuid.UUID] = Field(default=None)
    tenant_id: Optional[uuid.UUID] = Field(default=None)

    industry_document: Optional[list[object]] = Field(default=[{}])
    industry_name: Optional[str] = Field(default=None)


    class Config:
        orm_mode = True


class UpdateIndustry(BaseModel):
    industry_name: Optional[str] = Field(default=None)


    class Config:
        orm_mode = True


class ReadIndustries(BaseModel):
    data: list[Optional[ReadIndustry]]
    next_page: Union[str, int]
    page_size: int




class IndustriesAccess:
    related_access_roles = ['cybernetic-karari-industries-list', 'cybernetic-karari-industries-tenant-list', 'cybernetic-karari-industries-root-list', 'cybernetic-karari-documents-list', 'cybernetic-karari-documents-tenant-list', 'cybernetic-karari-documents-root-list']

    @classmethod
    def list_roles(cls):
        list_roles = ['cybernetic-karari-industries-list', 'cybernetic-karari-industries-tenant-list', 'cybernetic-karari-industries-root-list']
        return list(set(list_roles + cls.related_access_roles))

    @classmethod
    def create_roles(cls):
        create_roles = ['cybernetic-karari-industries-create', 'cybernetic-karari-industries-tenant-create', 'cybernetic-karari-industries-root-create']
        return create_roles + cls.related_access_roles

    @classmethod
    def update_roles(cls):
        update_roles = ['cybernetic-karari-industries-update', 'cybernetic-karari-industries-tenant-update', 'cybernetic-karari-industries-root-update']
        return update_roles + cls.related_access_roles

    @classmethod
    def delete_roles(cls):
        delete_roles = ['cybernetic-karari-industries-delete', 'cybernetic-karari-industries-tenant-delete', 'cybernetic-karari-industries-root-delete']
        return delete_roles + cls.related_access_roles