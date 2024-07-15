
from typing import Optional, List
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr, Field
from core.encrypt_str import EncryptStr



# select enums
class StatusEnum(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class CreateSummary_Task(BaseModel):
    id: Optional[uuid.UUID]
    status: StatusEnum
    questions: List[str]
    min_max: str
    word_count: str
    source: Optional[str] = Field(default=None)
    industry: Optional[List[str]]
    category: List[str]
    tags: Optional[List[str]]
    release_date: Optional[datetime.date] = Field(default=None)
    expiry_date: Optional[datetime.date] = Field(default=None)
    html: Optional[str] = Field(default=None)
    pdf: Optional[uuid.UUID] = Field(default=None)
    name: Optional[str] = Field(default=None)

    @validator('status')
    def validate_status(cls, status: StatusEnum):
        if False or False or False:
            raise ValueError(f"field <status> is not allowed")
        return status
    @validator('questions')
    def validate_questions(cls, questions: List[str]):
        if False or False or False:
            raise ValueError(f"field <questions> is not allowed")
        return questions
    @validator('min_max')
    def validate_min_max(cls, min_max: str):
        if False or False or False:
            raise ValueError(f"field <min_max> is not allowed")
        return min_max
    @validator('industry')
    def validate_industry(cls, industry: Optional[List[str]]):
        if False or False or False:
            raise ValueError(f"field <industry> is not allowed")
        return industry
    @validator('category')
    def validate_category(cls, category: List[str]):
        if False or False or False:
            raise ValueError(f"field <category> is not allowed")
        return category
    @validator('tags')
    def validate_tags(cls, tags: Optional[List[str]]):
        if False or False or False:
            raise ValueError(f"field <tags> is not allowed")
        return tags

class ReadSummary_Task(BaseModel):
    id: uuid.UUID
    created_on: datetime.datetime
    updated_on: datetime.datetime
    created_by: Optional[uuid.UUID] = Field(default=None)
    updated_by: Optional[uuid.UUID] = Field(default=None)
    tenant_id: Optional[uuid.UUID] = Field(default=None)
    status: StatusEnum
    questions: List[str]
    min_max: str
    word_count: str
    source: Optional[str] = Field(default=None)
    industry: Optional[List[str]]
    category: List[str]
    tags: Optional[List[str]]
    release_date: Optional[datetime.date] = Field(default=None)
    expiry_date: Optional[datetime.date] = Field(default=None)
    html: Optional[str] = Field(default=None)
    pdf: Optional[uuid.UUID] = Field(default=None)
    name: Optional[str] = Field(default=None)


    @validator('status')
    def validate_status(cls, status: StatusEnum):
        return status

    @validator('questions')
    def validate_questions(cls, questions: List[str]):
        return questions

    @validator('min_max')
    def validate_min_max(cls, min_max: str):
        return min_max

    @validator('industry')
    def validate_industry(cls, industry: Optional[List[str]]):
        return industry

    @validator('category')
    def validate_category(cls, category: List[str]):
        return category

    @validator('tags')
    def validate_tags(cls, tags: Optional[List[str]]):
        return tags

    class Config:
        orm_mode = True


class UpdateSummary_Task(BaseModel):
    status: Optional[StatusEnum] = Field(default=None)
    questions: Optional[List[str]]
    min_max: Optional[str] = Field(default=None)
    word_count: Optional[str] = Field(default=None)
    source: Optional[str] = Field(default=None)
    industry: Optional[List[str]]
    category: Optional[List[str]]
    tags: Optional[List[str]]
    release_date: Optional[datetime.date] = Field(default=None)
    expiry_date: Optional[datetime.date] = Field(default=None)
    html: Optional[str] = Field(default=None)
    pdf: Optional[uuid.UUID] = Field(default=None)
    name: Optional[str] = Field(default=None)


    @validator('status')
    def validate_status(cls, status: StatusEnum):
        if False or '__' in status or status in ['id']:
            raise ValueError(f"field <status> is not allowed")
        return status

    @validator('questions')
    def validate_questions(cls, questions: List[str]):
        if False or '__' in questions or questions in ['id']:
            raise ValueError(f"field <questions> is not allowed")
        return questions

    @validator('min_max')
    def validate_min_max(cls, min_max: str):
        if False or '__' in min_max or min_max in ['id']:
            raise ValueError(f"field <min_max> is not allowed")
        return min_max

    @validator('industry')
    def validate_industry(cls, industry: Optional[List[str]]):
        if False or '__' in industry or industry in ['id']:
            raise ValueError(f"field <industry> is not allowed")
        return industry

    @validator('category')
    def validate_category(cls, category: List[str]):
        if False or '__' in category or category in ['id']:
            raise ValueError(f"field <category> is not allowed")
        return category

    @validator('tags')
    def validate_tags(cls, tags: Optional[List[str]]):
        if False or '__' in tags or tags in ['id']:
            raise ValueError(f"field <tags> is not allowed")
        return tags

    class Config:
        orm_mode = True


class ReadSummary_Tasks(BaseModel):
    data: list[Optional[ReadSummary_Task]]
    next_page: Union[str, int]
    page_size: int




class Summary_TasksAccess:
    related_access_roles = ['cybernetic-karari-summary_tasks-list', 'cybernetic-karari-summary_tasks-tenant-list', 'cybernetic-karari-summary_tasks-root-list']

    @classmethod
    def list_roles(cls):
        list_roles = ['cybernetic-karari-summary_tasks-list', 'cybernetic-karari-summary_tasks-tenant-list', 'cybernetic-karari-summary_tasks-root-list']
        return list(set(list_roles + cls.related_access_roles))

    @classmethod
    def create_roles(cls):
        create_roles = ['cybernetic-karari-summary_tasks-create', 'cybernetic-karari-summary_tasks-tenant-create', 'cybernetic-karari-summary_tasks-root-create']
        return create_roles + cls.related_access_roles

    @classmethod
    def update_roles(cls):
        update_roles = ['cybernetic-karari-summary_tasks-update', 'cybernetic-karari-summary_tasks-tenant-update', 'cybernetic-karari-summary_tasks-root-update']
        return update_roles + cls.related_access_roles

    @classmethod
    def delete_roles(cls):
        delete_roles = ['cybernetic-karari-summary_tasks-delete', 'cybernetic-karari-summary_tasks-tenant-delete', 'cybernetic-karari-summary_tasks-root-delete']
        return delete_roles + cls.related_access_roles