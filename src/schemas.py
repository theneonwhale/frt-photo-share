import enum
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import List
from sqlalchemy import asc, desc
from src.conf.messages import MSC201_USER_CREATED, TOKEN_TYPE
from src.database.models import Role, TransformationsType


class UserModel(BaseModel):
    """User model class."""
    username: str = Field(min_length=2, max_length=30)
    email: EmailStr
    password: str = Field(min_length=6, max_length=14)


class UserType(UserModel):
    roles: str = 'user'  # Role


class UserDb(BaseModel):
    """Class User for DataBase."""
    id: int  # = 1
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        """Indicates that the UserDb model is used to represent the ORM model."""
        orm_mode = True


class UserResponse(BaseModel):
    """User response class."""
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str
    roles: Role
    detail: str = MSC201_USER_CREATED
    status_active: bool
    
    class Config:
        orm_mode = True


class UserResponseFull(UserResponse):
    """User full-response class."""
    number_images: int = 0


class TagModel(BaseModel):
    name: str = Field(max_length=20)


class TagResponse(TagModel):
    name: str

    class Config:
        orm_mode = True


class ImageModel(BaseModel):
    description: str = Field(max_length=50)
    tags: str


class ImageResponse(ImageModel):
    id: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse]

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = TOKEN_TYPE


class RequestEmail(BaseModel):
    email: EmailStr


class PasswordRecovery(BaseModel):  # #
    """To check the sufficiency of the password during the password recovery procedure."""
    password: str = Field(min_length=6, max_length=14)


class CommentModel(BaseModel):
    comment: str = Field(max_length=2000)


class CommentResponse(CommentModel):
    id: int

    class Config:
        orm_mode = True


class TransformateModel(BaseModel):
    Type: TransformationsType


class SortDirection(enum.Enum):
    up: str = 'asc'
    down: str = 'desc'
    