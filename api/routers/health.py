import logging
from enum import Enum
from typing import Optional
from fastapi import APIRouter, Form
from pydantic import BaseModel

from fastapi_versioning import version

logger = logging.getLogger(__name__)
router = APIRouter()


class Platform(str, Enum):
    ANDROID = 'A'
    IOS = 'I'


class VersionV1(BaseModel):
    platform: Optional[Platform]
    min_supported_version: Optional[str]
    latest_version: Optional[str]
    ai_version: Optional[str]
    ai_pro_version: Optional[str]


class VersionV2(BaseModel):
    platform: Optional[Platform]
    min_supported_version: Optional[str]
    latest_version: Optional[str]
    ai_version: Optional[str]
    ai_pro_version: Optional[str]
    is_server_check: str = 'n'
    server_check_title: str = ""
    server_check_desc: str = ""


# @router.get('/health')
# def health_check():
#     # just for connecting to db : MySQL Has gone away 방지
#     config_service.get_config('checkin_version')
#     return


# # ... => 필수필드.
# # user 필드는 애플과 서비스 최초 연동 시에만 넘어옴.
# @router.post('/apple-redirect')
# def apple_redirect(
#     state: Optional[str] = Form(...),
#     code: Optional[str] = Form(...),
#     id_token: Optional[str] = Form(...),
#     user: Optional[str] = Form(None),
# ):
#     result = {
#         'state': state,
#         'code': code,
#         'id_token': id_token,
#         'user': user,
#     }
#     return result
