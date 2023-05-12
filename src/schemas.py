from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import List

from src.conf.messages import MSC201_USER_CREATED


class UserModel(BaseModel):
    """User model class."""
    id: int  # = 0
    username: str = Field(min_length=2, max_length=30)
    email: EmailStr
    password: str = Field(min_length=6, max_length=14)


class UserDb(BaseModel):
    """Class User for DataBase."""
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        """Indicates that the UserDb model is used to represent the ORM model."""
        orm_mode = True


class UserResponse(UserModel):
    """User response class."""
    id: int
    user: UserDb
    detail: str = MSC201_USER_CREATED
    

    class Config:
        orm_mode = True


class TagModel(BaseModel):
    name: str = Field(max_length=20)


class TagResponse(TagModel):
    id: int

    class Config:
        orm_mode = True


class ImageModel(BaseModel):
    description: str = Field(max_length=50)
    link: str
    user_id: int
    tags: List[int]


class ImageResponse(ImageModel):
    id: int
    user_id: int
    link: str
    tags: List[TagResponse]

    class Config:
        orm_mode = True
