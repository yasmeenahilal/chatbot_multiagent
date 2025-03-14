from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from database.base import get_session
from schemas.user import CreateUser, UpdateUser, GetUser
from internal.user_service import UserService
from uuid import UUID

router = APIRouter()
user_service = UserService()

@router.get("/users", response_model=list[GetUser], status_code=status.HTTP_200_OK)
async def get_all_users(session: AsyncSession = Depends(get_session)):
    return await user_service.get_all_user(session)

@router.get("/users/{uid}", response_model=GetUser, status_code=status.HTTP_200_OK)
async def get_user(uid: UUID, session: AsyncSession = Depends(get_session)):
    return await user_service.get_user(uid, session)

@router.post("/users", response_model=GetUser, status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUser, session: AsyncSession = Depends(get_session)):
    return await user_service.create_user(user, session)

@router.put("/users/{uid}", response_model=GetUser, status_code=status.HTTP_200_OK)
async def update_user(uid: UUID, update: UpdateUser, session: AsyncSession = Depends(get_session)):
    return await user_service.update_user(uid, update, session)

@router.delete("/users/{uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(uid: UUID, session: AsyncSession = Depends(get_session)):
    await user_service.delete_user(uid, session)
    return None