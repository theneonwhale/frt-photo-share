from typing import List
from pydantic import BaseModel, Field


class UserModel(BaseModel):
    id: int
    # TODO


class UserResponse(UserModel):
    id: int

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
