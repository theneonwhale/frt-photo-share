# from datetime import date, timedelta
from typing import Optional

# from fastapi import HTTPException, status
# from fastapi.encoders import jsonable_encoder
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
# from sqlalchemy import cast, func, or_, String
from sqlalchemy.orm import Session

from src.database.models import Image, User
# from src.schemas import ImageModel


async def get_images(
                     user: User,  # !
                     db: Session,  # pagination_params: Page
                     pagination_params: Params
                     ) -> Page:
    # if user:
    return paginate(
                    query=db.query(Image)
                    # .filter(Image.user_id == user.id)
                    .order_by(Image.user_id),  # Image.updated_at & schemas...
                    params=pagination_params
                    )


async def get_image(
                    image_id: int, 
                    user: User,  # !
                    db: Session
                    ) -> Optional[Image]:

    return (
            db.query(Image)
            # .filter(Image.user_id == user.id)
            .filter_by(id=image_id)
            .first()
            )