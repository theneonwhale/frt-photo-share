import enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List

from src.database.models import TransformationsType


class TagModel(BaseModel):
    name: str = Field(max_length=20)

    class Config:
        orm_mode = True


class ImageModel(BaseModel):
    description: str = Field(max_length=50)
    tags: str
    rating: float = None


class ImageResponse(ImageModel):
    id: int
    link: str
    created_at: datetime
    updated_at: datetime
    tags: List[TagModel]
    rating: float = None

    class Config:
        orm_mode = True


class TransformateModel(BaseModel):
    Type: TransformationsType


class SortDirection(enum.Enum):
    up: str = 'asc'
    down: str = 'desc'


class CommentModel(BaseModel):
    comment: str = Field(max_length=2000)


class CommentResponse(CommentModel):
    id: int

    class Config:
        orm_mode = True


class RatingModel(BaseModel):
    rating: int = Field(ge=1, le=5)


class RatingResponse(RatingModel):
    id: int
    rating: int = Field(ge=1, le=5)

    class Config:
        orm_mode = True