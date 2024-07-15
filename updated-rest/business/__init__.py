import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from mongosql import MongoSqlBase
from sqlalchemy.orm import sessionmaker
from core.logger import log
from core.constants import AppConstants as AC


Base = declarative_base(cls=(MongoSqlBase,))

db_sync_url = f'{AC.DB_SYNC_DRIVER}://{AC.DB_USERNAME}:{AC.DB_PASSWORD}@{AC.DB_HOST}:{AC.DB_PORT}/{AC.DB_NAME}?{AC.SYNC_DB_QUERY_PARAMS}'

engine_args = {
    "pool_size": AC.DB_POOL_SIZE,
    "max_overflow": AC.DB_MAX_OVERFLOW,
    "pool_timeout": AC.DB_POOL_TIMEOUT,
    "pool_recycle": AC.DB_POOL_RECYCLE,
}

engine_sync = create_engine(db_sync_url, echo=True, **engine_args)
db_sync_session: Session = sessionmaker(bind=engine_sync, expire_on_commit=False)

from core.depends import current_user_roles, current_user_uuid, current_user_tenant
@event.listens_for(db_sync_session, 'after_begin')
def execute_after_begin_transaction(session, transaction, connection):
    log.debug('--- Start new transaction ----')
    session.execute(f"SET zekoder.id = '{current_user_uuid()}'")
    session.execute(f"SET zekoder.roles = '{','.join(current_user_roles())}'")
    session.execute(f"SET zekoder.tenant_id = '{current_user_tenant()}'")
    log.debug('--- Database parameters has been set ----')
