# from datetime import date, timedelta
from typing import Optional

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import asc, desc
# from sqlalchemy import cast, func, or_, String
from sqlalchemy.orm import Session

from src.database.models import Comment, Image, User, Tag, image_m2m_tag
from src.schemas import ImageModel, SortDirection
from src.conf.messages import *
from src.repository import tags as repository_tags


async def get_images(
                     user: dict,  # !
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
                    user: dict,  # !
                    db: Session
                    ) -> Optional[Image]:
    return (
            db.query(Image)
            # .filter(Image.user_id == user.id)
            .filter_by(id=image_id)
            .first()
            )


async def create_image(
                       body: dict,
                       user_id: int,
                       db: Session,
                       tags_limit: int
                       ) -> Image | Exception:
    tags_names = body['tags'].split()  # None? get...
    if len(tags_names) > tags_limit:  # 5
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=MSC409_TAGS)  # cut 5?
    
    tags = []
    for el in tags_names:
        tag = await repository_tags.get_tag_by_name(el, db)
        if tag is None:
            tag = await repository_tags.create_tag(el, db)

        tags.append(tag)
    try:
        image = Image(description=body['description'], link=body['link'], user_id=user_id, tags=tags)

    except Exception as er:
        return er

    db.add(image)
    db.commit()
    db.refresh(image)

    return image


async def transform_image(
                          body: dict,
                          user_id: int,
                          db: Session
                          ) -> Image:
    try:
        image = Image(
                      description=body['description'], 
                      link=body['link'], 
                      user_id=user_id, 
                      type=body['type'], 
                      tags=body['tags']
                      )

    except Exception as er:
        return er

    db.add(image)
    db.commit()
    db.refresh(image)

    return image


async def remove_image(
                       image_id: int,
                       user: dict,  # !
                       db: Session
                       ) -> Optional[Image]:
    # image = db.query(Image).filter(Image.user_id == user.id).filter_by(id=image_id).first()
    # if user.id == Image.user_id or user.rile ...
    image: Image = db.query(Image).filter_by(id=image_id, user_id=user['id']).first()
    if image:
        db.delete(image)
        db.commit()

    return image


# EDIT description image...
async def update_image(
                       image_id: int,
                       body: ImageModel,
                       user: dict,  # !
                       db: Session,
                       tags_limit: int
                       ) -> Optional[Image]:
    # .filter(Image.id == image_id)
    image: Image = db.query(Image).filter_by(id=image_id, user_id=user['id']).first()
    '''
    # FOR edit only description?:
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
    
    tags_names = body.tags.split()
    # if len(tags_names) > tags_limit:  # 5
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=MSC409_TAGS)  # cut 5?
    tags_names = tags_names[:tags_limit]
    
    tags = []
    for el in tags_names:
        tag = await repository_tags.get_tag_by_name(el, db)
        if tag is None:
            tag = await repository_tags.create_tag(el, db)

        tags.append(tag)
    
    body_data['tags'] = tags
    for field in db_obj_data:
        if field in body_data:
            setattr(image, field, body_data[field]) if field != 'link' else None  # or remove from ImageModel

    db.add(image)

    db.commit()
    db.refresh(image)

    return image


async def get_image_by_tag(tag, sort_direction, db):
    image_tag = db.query(image_m2m_tag).filter_by(tag_id=tag.id).all()
    images_id = [el[1] for el in image_tag]
    if sort_direction.value == 'desc':
        images = db.query(Image).filter(Image.id.in_((images_id))).order_by(desc(Image.created_at)).all()
    else:
        images = db.query(Image).filter(Image.id.in_((images_id))).order_by(asc(Image.created_at)).all()

    return images

async def get_image_by_user(user_id, sort_direction, db):

    if sort_direction.value == 'desc':
        images = db.query(Image).filter_by(user_id=user_id).order_by(desc(Image.created_at)).all()
    else:
        images = db.query(Image).filter_by(user_id=user_id).order_by(asc(Image.created_at)).all()

    return images