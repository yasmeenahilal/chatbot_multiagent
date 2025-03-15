from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    gender: Optional[str] = None
    age: Optional[int] = None


class CreateUser(UserBase):
    username: str = Field(max_length=16)
    password: str = Field(min_length=8)


class UpdateUser(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None


class GetUser(UserBase):
    uid: UUID
    created_at: datetime
    updated_at: datetime


class Login(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=8)
