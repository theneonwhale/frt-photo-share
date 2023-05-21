from typing import Optional

from fastapi import HTTPException, status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from src.database.models import Image, image_m2m_tag
from src.schemas.images import ImageModel
from src.conf import messages
from src.repository import tags as repository_tags


async def get_images(
                     user: dict,
                     db: Session,
                     pagination_params: Params
                     ) -> Page:
    """
    The get_images function returns a list of images.

    :param user: dict: Pass the user's information to the function
    :param db: Session: Access the database
    :param pagination_params: Params: Pass in the pagination parameters
    :return: A page object that contains the results of a paginated query
    :doc-author: Trelent
    """
    return paginate(
                    query=db.query(Image).order_by(Image.user_id),
                    params=pagination_params
                    )


async def get_image(
                    image_id: int, 
                    user: dict,
                    db: Session
                    ) -> Optional[Image]:
    """
    The get_image function returns an image object from the database.
    Args:
    image_id (int): The id of the desired image.
    user (dict): A dictionary containing a user's credentials and permissions.
    This is used to determine if a user has permission to view this particular
    resource, as well as for logging purposes.

    :param image_id: int: Specify the id of the image that we want to get
    :param user: dict: Pass the user information to the function
    :param db: Session: Pass the database session to the function
    :return: An image object
    :doc-author: Trelent
    """
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
    """
    The create_image function creates a new image in the database.
    Args:
    body (dict): The request body containing the image's description, link and tags.
    user_id (int): The id of the user who created this image.

    :param body: dict: Get the data from the request body
    :param user_id: int: Get the user_id from the token
    :param db: Session: Access the database
    :param tags_limit: int: Limit the number of tags that can be added to an image
    :return: The image created
    :doc-author: Trelent
    """
    tags_names = body['tags'].split()

    if len(tags_names) > tags_limit:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.MSC409_TAGS)
    
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
    """
    The transform_image function takes in a dictionary of image data, the user_id of the user who created it, and a database session.
    It then creates an Image object from that data and adds it to the database. It returns either an error or the newly created Image.

    :param body: dict: Pass the data from the request body
    :param user_id: int: Get the user id from the token
    :param db: Session: Access the database
    :return: A new image object
    :doc-author: Trelent
    """
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
                       user: dict,
                       db: Session
                       ) -> dict:
    """
    The remove_image function removes an image from the database.

    :param image_id: int: Specify the image to be deleted
    :param user: dict: Check if the user is an admin or moderator
    :param db: Session: Access the database
    :return: A message to the user
    :doc-author: Trelent
    """
    if user['roles'].value in ['admin', 'moderator']:
        image: Image = db.query(Image).filter_by(id=image_id).first()

    else:
        image: Image = db.query(Image).filter_by(id=image_id, user_id=user['id']).first()

    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)
    else:
        db.delete(image)
        db.commit()

    return {'message': messages.IMAGE_DELETED}


async def update_image(
                       image_id: int,
                       body: ImageModel,
                       user: dict,
                       db: Session,
                       tags_limit: int
                       ) -> Optional[Image]:
    """
    The update_image function updates an image in the database.

    :param image_id: int: Get the image by id
    :param body: ImageModel: Pass the image model to the function
    :param user: dict: Check if the user is an admin or a moderator
    :param db: Session: Pass the database session to the function
    :param tags_limit: int: Limit the number of tags that can be added to an image
    :return: The updated image
    :doc-author: Trelent
    """
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


async def get_images_by_tag(tag, sort_direction, db):
    """
    The get_images_by_tag function takes in a tag and a sort direction, and returns all images associated with that tag.
    The function first queries the image_m2m_tag table to find all rows where the tag id matches the inputted tags id.
    It then creates an array of image ids from those rows, which it uses to query for images in the Image table. It then sorts these images by creation date based on whether or not they were sorted ascendingly or descendingly.

    :param tag: Filter the images by tag
    :param sort_direction: Determine whether the images should be sorted in ascending or descending order
    :param db: Pass the database session to the function
    :return: A list of images that have a specific tag
    :doc-author: Trelent
    """
    image_tag = db.query(image_m2m_tag).filter_by(tag_id=tag.id).all()
    images_id = [el[1] for el in image_tag]
    if sort_direction.value == 'desc':
        images = db.query(Image).filter(Image.id.in_((images_id))).order_by(desc(Image.created_at)).all()

    else:
        images = db.query(Image).filter(Image.id.in_((images_id))).order_by(asc(Image.created_at)).all()

    return images


async def get_images_by_user(user_id, sort_direction, db):
    """
    The get_images_by_user function returns a list of images that are associated with the user_id passed in.
    The sort_direction parameter is an enum value that can be either 'asc' or 'desc'. The db parameter is a database session object.

    :param user_id: Filter the images by user_id
    :param sort_direction: Determine the order in which images are returned
    :param db: Pass in the database session object
    :return: A list of image objects
    :doc-author: Trelent
    """
    if sort_direction.value == 'desc':
        images = db.query(Image).filter_by(user_id=user_id).order_by(desc(Image.created_at)).all()

    else:
        images = db.query(Image).filter_by(user_id=user_id).order_by(asc(Image.created_at)).all()

    return images
