from datetime import datetime, timedelta, timezone
import os

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash


# --------------------------------------------------
# Configuration
# --------------------------------------------------

SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "CHANGE_THIS_SECRET_KEY"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


# --------------------------------------------------
# Password Hashing
# --------------------------------------------------

password_hash = PasswordHash.recommended()


# --------------------------------------------------
# OAuth2
# --------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login"
)


# --------------------------------------------------
# Demo Users
# --------------------------------------------------
# Prototype only.
# Production users should come from a database
# or an institutional identity provider.

USERS = {
    "admin": {
        "username": "admin",
        "password_hash": password_hash.hash("admin123"),
        "role": "admin"
    },

    "investigator": {
        "username": "investigator",
        "password_hash": password_hash.hash("investigator123"),
        "role": "investigator"
    }
}


# --------------------------------------------------
# Authenticate User
# --------------------------------------------------

def authenticate_user(username: str, password: str):

    user = USERS.get(username)

    if not user:
        return None

    if not password_hash.verify(
        password,
        user["password_hash"]
    ):
        return None

    return user


# --------------------------------------------------
# Create JWT
# --------------------------------------------------

def create_access_token(
    username: str,
    role: str
):

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": username,
        "role": role,
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# --------------------------------------------------
# Get Current User
# --------------------------------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")
        role = payload.get("role")

        if not username or not role:
            raise credentials_exception

        return {
            "username": username,
            "role": role
        }

    except jwt.PyJWTError:

        raise credentials_exception


# --------------------------------------------------
# Role Authorization
# --------------------------------------------------

def require_role(required_role: str):

    def role_checker(
        current_user=Depends(get_current_user)
    ):

        if current_user["role"] != required_role:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return current_user

    return role_checker