from database.redis import token_in_blocklist
from fastapi import Request, status, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from utils.utils import decode_token
from database.base import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from internal.user_service import UserService

user_service = UserService()

class TokenBearer(HTTPBearer):
    def __init__(
        self, *, bearerFormat=None, scheme_name=None, description=None, auto_error=True
    ):
        super().__init__(
            bearerFormat=bearerFormat,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials
        token_data = decode_token(token)
        if not self.token_valid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or expired",
                    "resolution": "Please get new token",
                },
            )
        if await token_in_blocklist(token_data["jti"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token has been revoked",
                    "resolution": "Please get new token",
                },
            )
        self.verify_token_data(token_data)
        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)
        if not token_data:
            return False
        return True

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("Please override this method in child classes method")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token",
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an refresh token",
            )


async def get_current_user(token_details: dict = Depends(AccessTokenBearer()),
                     session: AsyncSession = Depends(get_session)):
    print("\n\nTokenDetail", token_details)
    user_email = token_details['user']
    user = await user_service.get_user_by_email(user_email, session)
    return user