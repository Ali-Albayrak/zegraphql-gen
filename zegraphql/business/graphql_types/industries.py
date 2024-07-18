import datetime
from typing import Optional, TYPE_CHECKING, Union
import strawberry
from strawberry.permission import PermissionExtension

from .base import BaseType
from core.auth import Protect

@strawberry.input
class CreateIndustryInput(BaseType):
    industry_name: str
    id: Optional[strawberry.ID] = None

@strawberry.input
class UpdateIndustryInput(BaseType):
    industry_name: Optional[str] = None

