from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas.user import CreateUser, UpdateUser, GetUser
from model.user import User
from uuid import UUID
from datetime import datetime, timezone


class UserService:
    async def get_all_user(self, session: AsyncSession) -> list[GetUser]:
        try:
            statement = select(User).order_by(desc(User.created_at))
            result = await session.exec(statement)
            return result.all()
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def get_user(self, uid: UUID, session: AsyncSession) -> GetUser:
        try:
            statement = select(User).where(User.uid == uid)
            result = await session.exec(statement)
            user = result.first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {uid} not found",
                )
            return user
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def create_user(self, user: CreateUser, session: AsyncSession) -> GetUser:
        try:
            user_data = user.model_dump()
            new_user = User(**user_data)  # uid, created_at, updated_at are handled internally
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return new_user
        except IntegrityError as e:
            await session.rollback()
            if "duplicate key value violates unique constraint" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists",
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )
        except SQLAlchemyError as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def update_user(self, uid: UUID, update: UpdateUser, session: AsyncSession) -> GetUser:
        try:
            user_to_update = await self.get_user(uid, session)
            if not user_to_update:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {uid} not found",
                )
            update_data = update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(user_to_update, key, value)
            user_to_update.updated_at = datetime.now(timezone.utc)  # Update internally
            session.add(user_to_update)
            await session.commit()
            await session.refresh(user_to_update)
            return user_to_update
        except SQLAlchemyError as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )
    async def delete_user(self, uid: UUID, session: AsyncSession) -> None:
        try:
            user_to_delete = await self.get_user(uid, session)
            if not user_to_delete:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {uid} not found",
                )
            await session.delete(user_to_delete)
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )