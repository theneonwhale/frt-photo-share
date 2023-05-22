from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from src.conf import messages
from src.database.models import Role


class UserBase(BaseModel):
    username: str = Field(min_length=2, max_length=30)
    email: EmailStr


class UserModel(UserBase):
    password: str = Field(min_length=6, max_length=14)


class UserType(UserBase):
    roles: str = 'user'


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        """Indicates that the UserDb model is used to represent the ORM model."""
        orm_mode = True


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str
    roles: Role
    detail: str = messages.MSC201_USER_CREATED
    status_active: bool

    class Config:
        orm_mode = True


class UserResponseFull(UserResponse):
    number_images: int = 0


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = messages.TOKEN_TYPE


class RequestEmail(BaseModel):
    email: EmailStr


class PasswordRecovery(BaseModel):
    """To check the sufficiency of the password during the password recovery procedure."""
    password: str = Field(min_length=6, max_length=14)


class MessageResponse(BaseModel):
    message: str = Field(max_length=2000)
