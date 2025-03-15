from uuid import UUID

from config.security import AccessTokenBearer, RefreshTokenBearer
from database.base import get_session
from fastapi import APIRouter, Depends, status
from internal.user_service import UserService
from schemas.user import CreateUser, GetUser, Login, UpdateUser
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()
user_service = UserService()
access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()


@router.get("/users", response_model=list[GetUser], status_code=status.HTTP_200_OK)
async def get_all_users(
    session: AsyncSession = Depends(get_session),
    user_details=Depends(access_token_bearer),
):
    return await user_service.get_all_user(session)


@router.get("/users/{uid}", response_model=GetUser, status_code=status.HTTP_200_OK)
async def get_user(uid: UUID, session: AsyncSession = Depends(get_session)):
    return await user_service.get_user(uid, session)


@router.post("/singup", response_model=GetUser, status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUser, session: AsyncSession = Depends(get_session)):
    return await user_service.create_user(user, session)


@router.post("/login", response_model=GetUser, status_code=status.HTTP_201_CREATED)
async def login_user(user: Login, session: AsyncSession = Depends(get_session)):
    return await user_service.login_user(user, session)


@router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    return await user_service.get_new_access_token(token_details)


@router.put("/users/{uid}", response_model=GetUser, status_code=status.HTTP_200_OK)
async def update_user(
    uid: UUID, update: UpdateUser, session: AsyncSession = Depends(get_session)
):
    return await user_service.update_user(uid, update, session)


@router.delete("/users/{uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(uid: UUID, session: AsyncSession = Depends(get_session)):
    await user_service.delete_user(uid, session)
    return None
