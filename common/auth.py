from typing import Optional, Set
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBearer
from pydantic.main import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED
from auth.domain.entity import Auth
from auth.domain.entity.admin_auth import AdminAuth
from auth.entrypoints import service as auth_service
from common.exceptions import ApplicationError, AuthenticationError

http_scheme = HTTPBearer(auto_error=False)

# API 요청 시 인증토큰 선체크 함수 모음


class User(BaseModel):
    account_id: int
    email: str

    @classmethod
    def from_auth(cls, auth: Auth):
        return cls(account_id=auth.account_id, email=auth.email)


# 필수 인증
async def get_user(
    token: Optional[HTTPAuthorizationCredentials] = Depends(http_scheme),
) -> User:
    if not token:
        raise AuthenticationError(HTTP_401_UNAUTHORIZED, '로그인이 필요한 기능입니다.')

    try:
        auth = auth_service.get_auth(token.credentials)
    except ApplicationError:
        raise AuthenticationError(HTTP_401_UNAUTHORIZED, '로그인이 필요한 기능입니다.')
    return User.from_auth(auth)


# not 필수 인증
async def get_user_optional(
    token: Optional[HTTPAuthorizationCredentials] = Depends(http_scheme),
) -> Optional[User]:
    if not token:
        return None

    try:
        auth = auth_service.get_auth(token.credentials)
    except ApplicationError:
        return None
    return User.from_auth(auth)


# ADMIN AUTH START
class AdminUser(BaseModel):
    admin_id: int
    name: str
    roles: Set[str]
    is_approved: bool = False

    @classmethod
    def from_auth(cls, auth: AdminAuth):
        roles = set(auth.roles.split(',')) if auth.roles else set()
        return cls(
            admin_id=auth.id,
            name=auth.name,
            roles=roles,
            is_approved=auth.is_approved,
        )


async def get_admin_auth(
    token: Optional[HTTPAuthorizationCredentials] = Depends(http_scheme),
) -> AdminUser:
    if not token:
        raise AuthenticationError(HTTP_401_UNAUTHORIZED, '로그인이 필요한 기능입니다.')

    try:
        admin_auth = auth_service.get_admin_auth(token.credentials)
    except ApplicationError:
        raise AuthenticationError(HTTP_401_UNAUTHORIZED, '로그인이 필요한 기능입니다.')
    return AdminUser.from_auth(admin_auth)


async def get_admin_page_user(
    token: Optional[HTTPAuthorizationCredentials] = Depends(http_scheme),
) -> AdminUser:
    if not token:
        raise AuthenticationError(HTTP_401_UNAUTHORIZED, '로그인이 필요한 기능입니다.')

    """
    요청하는 기능과, 실제 그 기능을 실행할 수 있는 권한이 있는지 체크.
    TODO : 역할별 권한 세분화
    """

    admin_user = await get_admin_auth(token)
    return admin_user


# ADMIN AUTH END
