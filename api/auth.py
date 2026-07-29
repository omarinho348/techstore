import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext


JWT_SECRET_KEY = os.environ.get(
    "JWT_SECRET_KEY",
    "change-this-secret-in-production",
)

JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Hash a plain-text password.
    """

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    """
    Verify a plain-text password against its hash.
    """

    return pwd_context.verify(
        plain_password,
        password_hash,
    )


def create_access_token(
    customer_id: str,
) -> str:
    """
    Create a JWT access token for a customer.
    """

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    payload = {
        "sub": customer_id,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> str | None:
    """
    Decode a JWT and return the customer ID.
    """

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )

        customer_id = payload.get("sub")

        if not customer_id:
            return None

        return str(customer_id)

    except JWTError:
        return None