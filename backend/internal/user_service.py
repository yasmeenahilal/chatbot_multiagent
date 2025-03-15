from datetime import datetime, timedelta, timezone
from uuid import UUID

from config.settings import Config
from database.redis import add_jti_to_blocklist
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from model.user import User
from schemas.user import CreateUser, GetUser, Login, UpdateUser
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession
from utils.utils import create_access_token, generate_passwd_hash, verify_passwd


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

    async def get_user_by_email(self, email: str, session: AsyncSession) -> User:
        try:
            statement = select(User).where(User.email == email)
            result = await session.exec(statement)
            user = result.first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with email {email} not found",
                )
            return user  # Ensure returning User object, not a dict
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def create_user(self, user: CreateUser, session: AsyncSession) -> GetUser:
        try:
            user_data = user.model_dump()
            new_user = User(
                **user_data
            )  # uid, created_at, updated_at are handled internally
            new_user.role = "user"
            new_user.password_hash = generate_passwd_hash(user_data["password"])
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

    async def login_user(self, user: Login, session: AsyncSession) -> GetUser:
        try:

            email = user.email
            password = user.password

            # Fetch user from DB
            user = await self.get_user_by_email(email, session)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            # Verify Password
            password_valid = verify_passwd(password, user.password_hash)
            if not password_valid:
                raise HTTPException(status_code=401, detail="Invalid credentials")

            # Generate Tokens
            try:
                access_token = create_access_token(
                    {"email": user.email, "user_uid": str(user.uid), "role": user.role}
                )

                refresh_token = create_access_token(
                    {"email": user.email, "user_uid": str(user.uid)},
                    refresh=True,
                    expiry=timedelta(days=Config.REFRESH_TOKEN_VALIDITY),
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Token generation failed: {str(e)}"
                )

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": user.email,
                        "uid": str(user.uid),
                    },
                }
            )

        except HTTPException as http_exc:
            return JSONResponse(
                status_code=http_exc.status_code, content={"detail": http_exc.detail}
            )

        except Exception as e:
            return JSONResponse(
                status_code=500, content={"detail": f"Internal Server Error: {str(e)}"}
            )

    async def get_new_access_token(self, token_details: dict):
        try:
            expiry_timestamp = token_details.get("exp")
            user_data = token_details.get("user")
            token_details["email"] = token_details["user"]
            if not expiry_timestamp or not user_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token details",
                )

            # Convert expiry timestamp to datetime
            expiry_time = datetime.fromtimestamp(expiry_timestamp, timezone.utc)

            if expiry_time > datetime.now(timezone.utc):
                new_access_token = create_access_token(token_details)
                return JSONResponse(content={"access_token": new_access_token})

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Expired refresh token"
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating new access token: {str(e)}",
            )

    async def update_user(
        self, uid: UUID, update: UpdateUser, session: AsyncSession
    ) -> GetUser:
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

    # async def revoke_token(self, token_details: dict):
    #     jti = token_details["jti"]
    #     await add_jti_to_blocklist(jti)

    #     return JSONResponse(
    #         content={"message": "Logged Out Successfully"},
    #         status_code=status.HTTP_200_OK,
    #     )
    async def revoke_token(self, token_details: dict):
        try:
            jti = token_details.get("jti")
            if not jti:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token details",
                )

            # Add the JTI to the Redis blocklist
            await add_jti_to_blocklist(jti)

            return JSONResponse(
                content={"message": "Logged out successfully"},
                status_code=status.HTTP_200_OK,
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to revoke token: {str(e)}",
            )