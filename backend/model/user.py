from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String
from sqlalchemy.dialects import postgresql as pg
from datetime import datetime, timezone
import uuid
from uuid import UUID
from typing import Optional


class User(SQLModel, table=True):
    __tablename__ = "user"
    uid: UUID = Field(
        default_factory=lambda: str(uuid.uuid4()),  # Automatically generate a UUID
        primary_key=True
    )
    first_name: str
    last_name: str
    email: str = Field(
        sa_column=Column(String, unique=True, nullable=False)
    )
    gender: Optional[str] = None
    age: Optional[int] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False)
    )
    # is_verified: bool = False
    # is_active: bool = False
    # is_superuser: bool = False
    

    def __repr__(self):
        return f"<User(uuid={self.uuid}, first_name={self.first_name}, last_name={self.last_name}, email={self.email})>"