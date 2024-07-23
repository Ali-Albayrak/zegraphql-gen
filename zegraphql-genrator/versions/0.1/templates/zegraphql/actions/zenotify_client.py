import os
import httpx
from typing import List, Union
from core.logger import log
from core.constants import AppConstants


class ZeNotifyClient:

    def __init__(self, token):
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

    async def _call(self, url: str, payload: dict, failure_msg: str, success_msg: str) -> Union[dict, None]:
        """
        Abstract method for making a connection to ZeNotify using the specified HTTP method.

        Parameters:
            url (str): The URL of the API endpoint.
            failure_msg (str): Custom failure message for logging.
            payload (dict): The payload for the request.

        Returns:
            The response object if the request is successful, else None.
        """
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(url=url, json=payload, headers=self.headers)
                if res.status_code in [200, 201]:
                    log.info(success_msg)
                    return res.json()
                else:
                    log.debug(f"Status:{res.status_code}, {await res.json()}")
                    log.error(f"{failure_msg}, check the debug above!")
                    return None

        except httpx.RequestError as err:
            log.debug(err)
            log.error(f"RequestError while calling:<{url}>, check the debug above!")
            return None
        except httpx.HTTPStatusError as err:
            log.debug(err)
            log.error(f"HTTPStatusError while calling:<{url}>, check the debug above!")
            return None
        except Exception as err:
            log.debug(err)
            log.error(f"Unexpected error while calling:<{url}>, check the debug above!")
            return None

    async def create_notification(self, recipients: List[str], template: str, provider:str, params:List[dict], target:str) -> Union[dict, None]:
        """
        Create new notification in ZeNotify app
        """
        payload = {
            "recipients": recipients,
            "push_subscriptions": {},
            "provider": provider,
            "template": template,
            "params": {"list": params},
            "target": target,
            "status": "",
            "last_error": ""
        }
        return await self._call(
            url=f"{AppConstants.ZENOTIFY_BASE_URL}/notifications/",
            payload=payload,
            success_msg="New notification created successfully",            
            failure_msg="Unable to create notification"
        )
