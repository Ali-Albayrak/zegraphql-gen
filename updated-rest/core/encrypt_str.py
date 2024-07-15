from typing import Dict, Any
from pydantic.utils import update_not_none
from core.logger import log
from core.constants import AppConstants
import requests
import os

ZEAUTH_ENCRYPT_URI = f'{AppConstants.ZEAUTH_BASE_URL}/encrypt_str'

class EncryptStr:
    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        update_not_none(
            field_schema,
            type='string'
        )

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def encryptStr(cls, value):
        try:
            params = {
                'str_for_enc': f'{value}',
            }
            response = requests.post(ZEAUTH_ENCRYPT_URI, params=params)
            result = response.json()
            return result['encrypt_decrypt_str']
        except Exception as e:
            log.debug(e)
            log.error("Can not connect to encryption endpoint or something went wrong")
            exit(1)

    @classmethod
    def validate(cls, value: Any):
        return cls.encryptStr(value)
