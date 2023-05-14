# from datetime import date, timedelta
from typing import Optional

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
# from sqlalchemy import cast, func, or_, String
from sqlalchemy.orm import Session

from src.database.models import Comment, Image, User, Tag
from src.schemas import ImageModel, CommentModel
from src.conf.messages import *
from src.repository import tags as repository_tags


async def get_images(
                     user: User,  # !
                     db: Session,  # pagination_params: Page
                     pagination_params: Params
                     ) -> Page:
    # if user:    # .filter(Image.user_id == user.id)    # Image.updated_at & schemas...
    return paginate(
                    query=db.query(Image).order_by(Image.user_id),
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


async def create_image(
                       body,
                       user: User,
                       db: Session
                       ) -> Image:
    tags_names = body['tags'].split()
    if len(tags_names) > 5:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=MSC409_TAGS)
    tags = []
    for el in tags_names:
        tag = await repository_tags.get_tag_by_name(el, db)
        if tag is None:
            tag = await repository_tags.create_tag(el, db)
            tags.append(tag)
        else:
            tags.append(tag)

    image = Image(description=body['description'], link=body['link'], user_id=user.id, tags=tags)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


async def remove_image(
                       image_id: int,
                       user: User,  # !
                       db: Session
                       ) -> Optional[Image]:

    # image = db.query(Image).filter(Image.user_id == user.id).filter_by(id=image_id).first()
    # if user.id == Image.user_id or user.rile ...
    image: Image = db.query(Image).filter_by(id=image_id).first()
    if image:
        db.delete(image)
        db.commit()

    return image


# EDIT description image...
async def update_image(
                       image_id: int,
                       body: ImageModel,
                       user: User,  # !
                       db: Session
                       ) -> Optional[Image]:

    # .filter(Image.id == image_id)
    image: Image = db.query(Image).filter_by(id=image_id).first()  

    # FOR edit only description:
    if not image or not body.description:
        return None
    
    image.description = body.description
    # setattr(image, 'description', body.description)
    '''
    # FOR full edit image:
    db_obj_data: Optional[dict] = image.__dict__ if image else None
    # db_obj_data = jsonable_encoder(image) if image else None
    
    body_data: Optional[dict] = jsonable_encoder(body) if body else None
    
    if not db_obj_data or not body_data:
        return None

    for field in db_obj_data:
        if field in body_data:
            setattr(image, field, body_data[field])  # ! & Tags how? ... compendium's example

    db.add(image)
    '''        
    db.commit()
    db.refresh(image)

    return image


# Leave a comment...
async def to_comment(
                     body: CommentModel,
                     image_id: int,
                     user: User,
                     db: Session
                     ) -> Optional[Image]:
 
    image: Image = db.query(Image).filter_by(id=image_id).first()
    if image:
        comment = Comment(**body.dict(), user_id=user.id, image_id=image_id)  # or , user=user
        db.add(comment)
        db.commit()
        db.refresh(comment)

    else:
        return None

    return image
