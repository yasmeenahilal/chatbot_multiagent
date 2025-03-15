import logging
import uuid
from datetime import datetime, timedelta

import jwt
from config.settings import Config
from passlib.context import CryptContext

# Create a CryptContext for bcrypt
passwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_passwd_hash(password: str) -> str:
    """Generate a bcrypt hash for the given password."""
    return passwd_context.hash(password)


def verify_passwd(password: str, hash: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return passwd_context.verify(password, hash)


def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
):
    payload = {}
    payload["user"] = user_data["email"]
    payload["exp"] = datetime.now() + timedelta(seconds=Config.JWT_TOKEN_VALIDITY)
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh
    token = jwt.encode(
        payload=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM
    )
    return token


def decode_token(token: str):
    try:
        token_data = jwt.decode(
            jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None
