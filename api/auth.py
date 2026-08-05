import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.models.customer import Customer

from jose import JWTError, jwt
from passlib.context import CryptContext


JWT_SECRET_KEY = os.environ.get(
    "JWT_SECRET_KEY",
    "change-this-secret-in-production",
)

print("JWT SECRET:", JWT_SECRET_KEY)

JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

security = HTTPBearer()

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

    except JWTError as e:
        print("=" * 50)
        print("JWT ERROR:", repr(e))
        return None

async def get_current_customer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Customer:

    print("=" * 50)
    print("Authorization header received")
    print(credentials.credentials)

    token = credentials.credentials

    customer_id = decode_access_token(token)

    print("Decoded customer_id:", customer_id)

    if customer_id is None:
        print("JWT decoding failed")

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token.",
        )

    customer = await Customer.get(customer_id)

    print("Customer:", customer)

    if customer is None:

        print("Customer not found")

        raise HTTPException(
            status_code=401,
            detail="Customer not found.",
        )

    return customer