from __future__ import annotations

from enum import Enum
import traceback
from typing import List, Optional

from common.msg import Button
# from common.slack import SLACK_API_TOKEN, SlackAPI


class ApplicationError(Exception):
    status_code = 400

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self,
        code: int,  # HTTP 에러코드
        message: str = "",  # 고객에게 보이는 메시지 : 제목
        description: str = "",  # 고객에게 보이는 메시지 : 본문
        data: Optional[str] = "",  # 에러 당시의 상황을 설명하는 변수
        btns: List[Button] = [],
        errors: List[ApplicationError] = [],
    ):

        super(ApplicationError, self).__init__(message)
        self.code = code
        self.message = message
        self.description = description
        self.data = data
        self.btns = btns
        self.errors = errors

        if code == 500:
            # 서버 에러만 슬랙
            # 에러 로그는 exception이 아니면 None으로 나옴
            slack = SlackAPI(SLACK_API_TOKEN)
            slack.post_message(
                text=f'오류 발생 : \n 관련 데이터 : {data} \n 메시지 : {message} \n 에러 로그 : {traceback.format_exc()}',
                channel_id="금손-시스템-알림",
            )

    def to_dict(self):
        result = {
            "code": self.code,
            "message": self.message,
        }
        if self.description:
            result["description"] = self.description
        if self.btns:
            result["btns"] = [btn.to_dict() for btn in self.btns]
        if self.errors:
            result["errors"] = [error.to_dict() for error in self.errors]
        return result


class AuthenticationError(ApplicationError):
    status_code = 401


class AuthorizationError(ApplicationError):
    status_code = 403


class ErrorCode(int, Enum):
    APPLICATION_ERROR = 400
    PRICE_LACK = 4001
    INTERNAL_SERVER_ERROR = 500

    NOT_AUTHENTICATED = 401
    INVALID_SESSION = 401

    NOT_AUTHORIZED = 403

    ACCOUNT_NOT_EXISTS = 404
    NOT_EXISTS = 404

    DUPLICATE_ENTRY = 409
    DUPLICATE_ENTRY_NAME = 4091
    DUPLICATE_ENTRY_EMAIL = 4092
    DUPLICATE_ENTRY_PHONE = 4093
    DUPLICATE_ENTRY_NICK_NAME = 4094
    DUPLICATE_START_SHOOTING = 444
    DUPLICATE_END_SHOOTING = 445
    DELETED_ACCOUNT = 410

    VALIDATION = 422
    INVALID_TOKEN = 422
    EXPIRED_TOKEN = 422
