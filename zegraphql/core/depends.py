import asyncio
import json
import uuid
import jwt
from contextvars import ContextVar
from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi.context import BaseContext

from .db_config import db_session 
from .logger import log
from .constants import AppConstants as AC


user_session: ContextVar[str] = ContextVar('user_session', default=None)
user_roles: ContextVar[list] = ContextVar('user_roles', default=[])
tenant_id: ContextVar[list] = ContextVar('tenant_id', default=None)

async def get_db():
    from sqlalchemy.sql import text
    from sqlalchemy import event
    from sqlalchemy.orm import Session
    from sqlalchemy.engine import Connection
    def execute_after_begin_transaction(session, transaction, connection: Connection):
        log.debug('--- Start new transaction ----')
        # session.execute(text(f"SET zekoder.id = '{current_user_uuid()}'"))
        # session.execute(text(f"SET zekoder.roles = '{','.join(current_user_roles())}'"))
        # session.execute(text(f"SET zekoder.tenant_id = '{current_user_tenant()}'"))
        # asyncio.run(session.execute(text(f"SET zekoder.id = '{current_user_uuid()}'")))
        # asyncio.run(session.execute(text(f"SET zekoder.roles = '{','.join(current_user_roles())}'")))
        # asyncio.run(session.execute(text(f"SET zekoder.tenant_id = '{current_user_tenant()}'")))
        # session.connection().execute(text(f"SET zekoder.id = '{current_user_uuid()}'"))
        # session.connection().execute(text(f"SET zekoder.roles = '{','.join(current_user_roles())}'"))
        # session.connection().execute(text(f"SET zekoder.tenant_id = '{current_user_tenant()}'"))
        # session.begin_nested().execute(text(f"SET zekoder.id = '{current_user_uuid()}'"))
        # session.begin_nested().execute(text(f"SET zekoder.roles = '{','.join(current_user_roles())}'"))
        # session.begin_nested().execute(text(f"SET zekoder.tenant_id = '{current_user_tenant()}'"))
        # log.debug(f"{session=}")
        # log.debug(f"{transaction=}")
        # tran = session.get_transaction()
        # engin = session.get_bind()
        # con = engin.connect()
        log.debug(f"{connection=}")
        log.debug(f"{type(connection)=}")
        log.debug(f"{dir(connection)=}")
        connection.execute(text(f"SET zekoder.id = '{current_user_uuid()}'"))
        connection.execute(text(f"SET zekoder.roles = '{','.join(current_user_roles())}'"))
        connection.execute(text(f"SET zekoder.tenant_id = '{current_user_tenant()}'"))
#         session.execute(text(f"""SET zekoder.id = '{current_user_uuid()}';
# SET zekoder.roles = '{','.join(current_user_roles())}';
# SET zekoder.tenant_id = '{current_user_tenant()}';
#                              """))
        log.debug('--- Database parameters has been set ----')


    async with db_session() as session:
        try:
            event.listen(
                session.sync_session,
                'after_begin',
                execute_after_begin_transaction
            )
            yield session

        finally:
            await session.close()


class GraphQLContext(BaseContext):
    def __init__(self, request: Request, db: AsyncSession):
        self.db = db
        # log.debug(f"{request=}")
        # log.debug(f"{dir(request)=}")
        self.request = request

async def get_context(request: Request, db: AsyncSession = Depends(get_db)) -> GraphQLContext:
    # js = await request.json()
    # q = js['query']
    # # parse the json
    # query = json.load(q)
    # log.debug(f"{query=}")
    # log.debug(f"{dir(request.json())=}")
    return GraphQLContext(request, db)

def set_current_user_data_contextvar(token: str, current_user_roles: list[str]) -> None:
        """
        Extracts the current user information from the authentication token and sets it in context variables.

        Parameters:
        - token (str): The authentication token.
        - current_user_roles (list[str]): The list of roles assigned to the current user.

        Raises:
        - HTTPException: Raises HTTPException with a 403 status code and an error message if the user information
                         cannot be extracted or if there's an issue setting context variables.
        """
        try:
            # current_user = jwt.decode(token, options={"verify_signature": False})
            current_user = {
                "sub": "b99b9894-384f-11ef-9e6b-177c65b0dbc4",
                "tenant_id": "f8aae1e6-ec07-11ee-9ea7-b7854b0d0692",
                "roles": ["cybernetic-karari-documents-create", "cybernetic-karari-documents-list"]
            } # replace this with the actual jwt.decode(token, options={"verify_signature": False})
            current_user_id = current_user.get("sub")
            current_user_tenant = current_user.get("tenant_id")
            if not current_user_id:
                raise HTTPException(403, "JWT token does not contians <id>")
            user_session.set(current_user_id)
            user_roles.set(current_user_roles)
            tenant_id.set(current_user_tenant)
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format("set_current_user_data_contextvar", type(e), str(e)))
            log.error(f"Unkown Session Error, Check the logs. Error: {e}")
            raise e

def current_user_uuid() -> str:
    """
    get current user uuid from contextvar
    """
    return user_session.get()

def current_user_tenant() -> str:
    """
    get current user uuid from contextvar
    """
    return tenant_id.get()

def current_user_roles() -> list:
    """
    get current user roles from contextvar
    """
    return user_roles.get()