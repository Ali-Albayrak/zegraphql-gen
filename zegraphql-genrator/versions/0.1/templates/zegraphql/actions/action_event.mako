% if type == 'notification':
from .zenotify_client import ZeNotifyClient
from core.constants import constants
from typing import List
import httpx
import asyncio

import os
from fastapi import HTTPException

<%
  def generate_validation_statment(validation):
    return f"if {validation}:" if validation else ""

  def generate_recipients(recipient):
    match recipient:
      case "user":
        return """
    user_email = await get_user_email(jwt)
    recipients = [user_email]"""
      case "admin":
        return """
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    recipients = [ADMIN_EMAIL]"""
      case "both":
        return """
    user_email = await get_user_email(jwt)
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    recipients = [user_email, ADMIN_EMAIL]"""
%>

% if options['recipient'] in ["admin", "both"]:
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
if ADMIN_EMAIL is None:
    raise ValueError("ADMIN_EMAIL environment variable is not set. Please set it before running the application.")
% endif

async def handler(
  jwt: dict,
  new_data: dict,
  old_data: dict,
  well_known_urls: dict,
  method: str = ""
) -> None:
  ${generate_validation_statment(validation)}
  ${generate_recipients(options['recipient'])}
    requried_params = prepare_params(new_data)
    await init_notification(recipients, requried_params)

% if options['recipient'] in ["user", "both"]:
async def get_user_email(token: str) -> str:
    """
    Verify the request token and extract email from it.
    """
    try:
        async with httpx.AsyncClient() as client:
            verify_res = await client.post(f"{constants.ZEAUTH_BASE_URL}/verify?token={token}", data={})
            if verify_res.status_code != 200:
                raise ValueError("invalid token")

            return verify_res.json()['email']
    except Exception as err:
        raise Exception(f"Error while verifying token: {err}, can not send notification")
% endif

def prepare_params(new_data) -> List[dict]:
  """
  Prepare required parameters for notification template.
  """
  requried_params = []
  for param in ${options['params']}:
    for param_name, field_name in param.items():
      requried_params.append({
        param_name : new_data.get(field_name)
      })
  return requried_params

async def init_notification(recipients: List[str], requried_params: List[dict]) -> None:
  """
  Create new notification in ZeNotify and kick it to the recipient via ZeNotify service.
  """
  zenotify = ZeNotifyClient(None)
  await zenotify.create_notification(
      recipients=recipients,
      template="${options['template']}",
      provider="${options['provider']}",
      target="${options['channel']}",
      params=requried_params
    )
% endif

% if type == 'event':
import json
from dapr.clients import DaprClient
from core.logger import log


def handler(jwt:dict, new_data: dict, old_data: dict, well_known_urls:list[str], method: str = ""):
  with DaprClient() as client:
      try:
        client.publish_event(
              pubsub_name='${pubsub}',
              topic_name='${target}-${channel}-channel',
              data=json.dumps({"new_data": new_data, "old_data": old_data, "action": method}),
              data_content_type='application/json',
        )
      except Exception as e:
        log.debug(e)
        log.error("cannot send message to ${target}-${channel}-channel triggered by create action for table apps")
% endif