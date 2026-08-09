from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """
    Request body for creating a customer account.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


class LoginRequest(BaseModel):
    """
    Request body for customer login.
    """

    email: EmailStr

    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
    )


class AuthResponse(BaseModel):
    """
    Authentication response.
    """

    customer_id: str

    name: str

    email: EmailStr

    created_at: datetime

    updated_at: datetime

    access_token: str

    token_type: str = "bearer"


class CustomerProfileResponse(BaseModel):
    """
    Profile data for the current customer.
    """

    customer_id: str

    name: str

    email: EmailStr

    created_at: datetime

    updated_at: datetime


class UpdateProfileRequest(BaseModel):
    """
    Request body for updating the current customer's profile.
    """

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    email: EmailStr | None = None

    current_password: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
    )

    new_password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
    )