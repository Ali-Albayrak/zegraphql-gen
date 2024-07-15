import uuid
from datetime import datetime

from business import Base
from core.depends import current_user_uuid, current_user_tenant
from sqlalchemy import Column, String, DateTime, func, Text, DATETIME, INTEGER
from sqlalchemy.dialects.postgresql import UUID


class BaseModel(Base):
    """
    Default fileds for any table 
    """
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(UUID(as_uuid=True), default=current_user_tenant)
    created_by = Column(UUID(as_uuid=True), default=current_user_uuid)
    updated_by = Column(UUID(as_uuid=True), default=current_user_uuid, onupdate=current_user_uuid)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class TenantModel(Base):
    __tablename__ = 'tenants'
    __table_args__ = {'schema': 'zekoder_zeauth'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(Text, nullable=False)
    created_on = Column(DATETIME, default=datetime.now())
    updated_on = Column(DATETIME, default=datetime.now(), onupdate=datetime.now())


class UserModel(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'zekoder_zeauth'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(Text, nullable=False)
    created_on = Column(DATETIME, default=datetime.now())
    updated_on = Column(DATETIME, default=datetime.now(), onupdate=datetime.now())


class FilesModel(Base):
    __tablename__ = 'files'
    __table_args__ = {'schema': 'public'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()))
    minio_address = Column(String, nullable=False)
    minio_thumbnail_address = Column(String)
    width = Column(INTEGER)
    height = Column(INTEGER)
    tn_width = Column(INTEGER)
    tn_height = Column(INTEGER)
    file_size = Column(INTEGER, nullable=False)
    file_name = Column(String, nullable=False)
    file_extension = Column(String)
    file_description = Column(String)
    created_on = Column(DATETIME, default=datetime.now())
    updated_on = Column(DATETIME, default=datetime.now(), onupdate=datetime.now())