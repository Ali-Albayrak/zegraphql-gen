import os
import uuid
import jwt
from contextvars import ContextVar
from typing import Optional, List, Union, Any

import requests as prequest
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from business import db_sync_session
from core.logger import log
from core.constants import AppConstants

auth_schema = HTTPBearer()

zeauth_url = AppConstants.ZEAUTH_BASE_URL
if zeauth_url is None:
    raise ValueError("ZEAUTH_URI environment variable is not set. Please set it before running the application.")

user_session: ContextVar[str] = ContextVar('user_session', default=None)
user_roles: ContextVar[list] = ContextVar('user_roles', default=[])
tenant_id: ContextVar[list] = ContextVar('tenant_id', default=None)

def get_sync_db():
    """
    Return sync engine to interact with datbase
    """
    db = db_sync_session()
    try:
        yield db
    finally:
        db.close()


class CommonDependencies:
    def __init__(self, page: Optional[str] = 1, size: Optional[int] = 20):
        self.page = page
        self.size = size
        self.offset = (int(page)-1) * int(size)


class Protect:
    def __init__(self, token: str = Depends(auth_schema), db: Session = Depends(get_sync_db)) -> None:
        self.credentials = token.credentials
        self.db = db

    def auth(self, method_required_roles: List[str])-> Union[None, dict]:
        """
        Authenticates the user based on the provided token and checks if the user has the required roles.

        Parameters:
        - method_required_roles (List[str]): A list of roles required to perform the action.

        Returns:
        - Union[None, dict]: The response from the authentication request.

        Raises:
        - HTTPException: Raises HTTPException with a 403 status code and an error message if authentication fails
                        or if the user is not authorized.
        """
        response = prequest.request("POST", f"{zeauth_url}/oauth/auth?token={self.credentials}", json={
            "roles": method_required_roles
        })
        if response.status_code != 200:
            raise HTTPException(403, "Invalid token")
        
        current_user_roles = response.json().get('allowed_roles', [])
        if not any(role in current_user_roles for role in method_required_roles):
            raise HTTPException(403, "User not authorized to perform this action")
        
        self.set_current_user_data_contextvar(current_user_roles)
        return response

    def set_current_user_data_contextvar(self, current_user_roles: list) -> None:
        """
        Extracts the current user information from the authentication response and sets it in context variables.

        Parameters:
        - response (Any): The response from the authentication request.

        Raises:
        - HTTPException: Raises HTTPException with a 403 status code and an error message if the user information
                         cannot be extracted or if there's an issue setting context variables.
        """
        try:
            current_user = jwt.decode(self.credentials, options={"verify_signature": False})
            current_user_id = current_user.get("sub")
            current_user_tenant = current_user.get("tenant_id")
            if not current_user_id:
                raise HTTPException(403, "JWT token does not contians <id>")
            user_session.set(current_user_id)
            user_roles.set(current_user_roles)
            tenant_id.set(current_user_tenant)
        except Exception as e:
            log.debug(e)
            raise HTTPException(403, "user not authorized to do this action")


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