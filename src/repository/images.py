from typing import Optional

from fastapi import HTTPException, status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from src.database.models import Image, image_m2m_tag
from src.schemas import ImageModel
from src.conf.messages import *
from src.repository import tags as repository_tags


async def get_images(
                     user: dict,  # !
                     db: Session,
                     pagination_params: Params
                     ) -> Page:
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
            .filter_by(id=image_id)
            .first()
            )


async def create_image(
                       body: dict,
                       user_id: int,
                       db: Session,
                       tags_limit: int
                       ) -> Image | Exception:
    tags_names = body['tags'].split()
    if len(tags_names) > tags_limit:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=MSC409_TAGS)

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
    if user['roles'].value in ['admin', 'moderator']:
        image: Image = db.query(Image).filter_by(id=image_id).first()

    else:
        image: Image = db.query(Image).filter_by(id=image_id, user_id=user['id']).first()

    if image:
        db.delete(image)
        db.commit()

    return image


async def update_image(
                       image_id: int,
                       body: ImageModel,
                       user: dict,  # !
                       db: Session,
                       tags_limit: int
                       ) -> Optional[Image]:
    if user['roles'].value in ['admin', 'moderator']:
        image: Image = db.query(Image).filter_by(id=image_id).first()

    else:
        image: Image = db.query(Image).filter_by(id=image_id, user_id=user['id']).first()

    if not image or not body.description:
        return None

    image.description = body.description

    tags_names = body.tags.split()[:tags_limit]

    tags = []
    for el in tags_names:
        tag = await repository_tags.get_tag_by_name(el, db)
        if tag is None:
            tag = await repository_tags.create_tag(el, db)

        tags.append(tag)

    image.tags = tags

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
