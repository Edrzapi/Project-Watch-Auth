from datetime import datetime
from typing import Optional

from pydantic import BaseModel, constr
from pydantic import validator


class UserBase(BaseModel):
    username: constr(min_length=1, max_length=50)  # Username must be between 1 and 50 characters


class UserProfileResponse(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        from_attributes = True  # Allows ORM models to be converted into Pydantic models


class UserFullResponse(UserBase):
    user_id: int
    password_hash: str  # Optionally, you could remove this for security reasons
    is_active: bool
    created_at: datetime
    updated_at: datetime
    profile: Optional[UserProfileResponse] = None  # Include profile details (first_name, last_name)

    class Config:
        from_attributes = True  # Use from_attributes to map the ORM models to Pydantic models


class UserCreate(UserBase):
    password: constr(min_length=8)  # Password must be at least 8 characters long
    first_name: Optional[str] = None  # Include first_name
    last_name: Optional[str] = None  # Include last_name

    @validator("password")
    def validate_password(cls, password):
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in password):
            raise ValueError("Password must contain at least one lowercase letter")
        return password


class UserUpdate(BaseModel):
    username: Optional[constr(min_length=1, max_length=50)] = None  # Optional username
    password: Optional[constr(min_length=8)] = None  # Optional password
    is_active: Optional[bool] = None  # Optional is_active flag
    first_name: Optional[str] = None  # Include first_name
    last_name: Optional[str] = None  # Include last_name

    @validator("password")
    def validate_password(cls, password):
        if password and len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if password and not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit")
        if password and not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if password and not any(char.islower() for char in password):
            raise ValueError("Password must contain at least one lowercase letter")
        return password


class User(UserBase):
    user_id: int
    password_hash: str  # Store hashed password
    created_at: datetime
    updated_at: datetime
    profile: Optional[UserProfileResponse] = None  # Include profile details (first_name, last_name)

    class Config:
        from_attributes = True  # Use `orm_mode` for compatibility with ORMs
