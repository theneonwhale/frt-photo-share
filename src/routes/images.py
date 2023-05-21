from typing import Optional, List

from fastapi import APIRouter, Depends, File, HTTPException, Path, Security, status, UploadFile
from fastapi_limiter.depends import RateLimiter
from fastapi_pagination import add_pagination, Page, Params
from fastapi.security import HTTPAuthorizationCredentials
from starlette.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.conf import messages
from src.database.db import get_db
from src.database.models import Image, TransformationsType
from src.repository import images as repository_images
from src.repository import tags as repository_tags
from src.repository import users as repository_users
from src.schemas.images import ImageModel, ImageResponse, SortDirection
from src.schemas.users import MessageResponse
from src.services.auth import AuthUser, security
from src.services.images import CloudImage
from src.services.roles import allowed_all_roles_access, allowed_admin_moderator


router = APIRouter(prefix='/images', tags=['images'])


@router.get(
            '/',
            description=f'Get images.\nNo more than {settings.limit_crit} requests per minute.',
            dependencies=[
                          Depends(allowed_all_roles_access),
                          Depends(RateLimiter(times=settings.limit_crit, seconds=settings.limit_crit_timer))
                          ],
            response_model=Page
            )
async def get_images(
                       db: Session = Depends(get_db),
                       current_user: dict = Depends(AuthUser.get_current_user),
                       credentials: HTTPAuthorizationCredentials = Security(security),
                       pagination_params: Params = Depends()
                       ) -> Page:
    """
    The get_images function returns a list of images.

    :param db: Session: Get the database session
    :param current_user: dict: Get the current user from the database
    :param credentials: HTTPAuthorizationCredentials: Authenticate the user
    :param pagination_params: Params: Get the pagination parameters from the request
    :return: A page object, which is a paginated list of image objects
    :doc-author: Trelent
    """
    images = await repository_images.get_images(current_user, db, pagination_params)

    return images


@router.post(
             '/transformation/{image_id}',
             description=f'Transform image.\nNo more than {settings.limit_crit} requests per minute.',
             dependencies=[
                           Depends(allowed_all_roles_access),
                           Depends(RateLimiter(times=settings.limit_crit, seconds=settings.limit_crit_timer))
                           ],
             response_model=ImageResponse
             )
async def transform_image(
                          type: TransformationsType,
                          image_id: int = Path(ge=1),
                          db: Session = Depends(get_db),
                          current_user: dict = Depends(AuthUser.get_current_user),
                          credentials: HTTPAuthorizationCredentials = Security(security)
                          ) -> Optional[Image]:
    """
    The transform_image function is used to transform an image.
    The function takes in the following parameters:
    - type: TransformationsType, which is a transformation type from the enum TransformationsType.
    - image_id: int = Path(ge=0), which is an integer representing the id of an existing image.
    This parameter must be greater than or equal to 1 and it's required for this function to work properly.

    :param type: TransformationsType: Define the type of transformation that will be applied to the image
    :param image_id: int: Get the image from the database
    :param db: Session: Get the database session
    :param current_user: dict: Get the user id of the current user
    :param credentials: HTTPAuthorizationCredentials: Validate the token
    :return: A new image with the transformation applied
    :doc-author: Trelent
    """
    image = await repository_images.get_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)
    if image.user_id != current_user['id']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.MSC400_BAD_REQUEST)

    transform_image_link = CloudImage.transformation(image, type)

    body = {
            'description': image.description,
            'link': transform_image_link,
            'tags': image.tags,
            'type': type.value
            }
    new_image = await repository_images.transform_image(body, image.user_id, db)

    return new_image


@router.get(
            '/qrcode/{image_id}',
            description=f'No more than {settings.limit_crit} requests per minute',
            dependencies=[
                           Depends(allowed_all_roles_access),
                           Depends(RateLimiter(times=settings.limit_crit, seconds=settings.limit_crit_timer))
                           ]
            )
async def image_qrcode(
                       image_id: int = Path(ge=1),
                       db: Session = Depends(get_db),
                       current_user: dict = Depends(AuthUser.get_current_user),
                       credentials: HTTPAuthorizationCredentials = Security(security),
                       ):
    """
    The image_qrcode function returns a QR code for the image.

    :param image_id: int: Identify the image that is to be deleted
    :param db: Session: Access the database
    :param current_user: dict: Get the current user's information
    :param credentials: HTTPAuthorizationCredentials: Authenticate the user
    :param : Get the image id from the url
    :return: A qr code for the image that can be used to download it
    :doc-author: Trelent
    """
    image = await repository_images.get_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)

    qr_code = CloudImage.get_qrcode(image)

    return StreamingResponse(qr_code, media_type="image/png")


@router.get(
            '/{image_id}',
            description=f'Get image.\nNo more than {settings.limit_warn} requests per minute.',
            dependencies=[
                          Depends(allowed_all_roles_access),
                          Depends(RateLimiter(times=settings.limit_warn, seconds=settings.limit_crit_timer))
                          ],
            response_model=ImageResponse
            )
async def get_image(
                    image_id: int = Path(ge=1),
                    db: Session = Depends(get_db),
                    current_user: dict = Depends(AuthUser.get_current_user),
                    credentials: HTTPAuthorizationCredentials = Security(security)
                    ) -> Optional[Image]:
    """
    The get_image function is used to retrieve a single image from the database.
    The function takes in an image_id, which is the id of the desired image. The function also takes in a db session,
    which will be used to query for images within the database. The current_user and credentials are required by FastAPI's
    security system.

    :param image_id: int: Get the image id from the path
    :param db: Session: Get a database session
    :param current_user: dict: Get the current user
    :param credentials: HTTPAuthorizationCredentials: Validate the authentication token
    :return: A single image object
    :doc-author: Trelent
    """
    image = await repository_images.get_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)

    return image


@router.post(
            '/',
            description=f'Create image.\nNo more than {settings.limit_warn} requests per minute.',
            dependencies=[
                          Depends(allowed_all_roles_access),
                          Depends(RateLimiter(times=settings.limit_warn, seconds=settings.limit_crit_timer))
                          ],
            response_model=ImageResponse
            )
async def create_image(
                       description: str = '-',
                       tags: str = '',
                       file: UploadFile = File(),
                       db: Session = Depends(get_db),
                       current_user: dict = Depends(AuthUser.get_current_user),
                       credentials: HTTPAuthorizationCredentials = Security(security)
                       ) -> Image:
    """
    The create_image function creates a new image in the database.

    :param description: str: Set the description of the image
    :param tags: str: Pass the tags for the image
    :param file: UploadFile: Upload the file to cloudinary
    :param db: Session: Access the database
    :param current_user: dict: Get the current user from the database
    :param credentials: HTTPAuthorizationCredentials: Authenticate the user
    :return: The created image object
    :doc-author: Trelent
    """
    public_id = CloudImage.generate_name_image(current_user.get('email'), file.filename)
    r = CloudImage.image_upload(file.file, public_id)
    src_url = CloudImage.get_url_for_image(public_id, r)
    body = {
            'description': description,
            'link': src_url,
            'tags': tags
            }
    image = await repository_images.create_image(body, current_user.get('id'), db, settings.tags_limit)

    return image


@router.delete(
               '/{image_id}',
               description=f'Remove image.\nNo more than {settings.limit_crit} requests per minute.',
               dependencies=[
                             Depends(RateLimiter(times=settings.limit_warn, seconds=settings.limit_crit_timer))
                             ],
               response_model=MessageResponse
               )
async def remove_image(
                       image_id: int = Path(ge=1),
                       db: Session = Depends(get_db),
                       current_user: dict = Depends(AuthUser.get_current_user),
                       credentials: HTTPAuthorizationCredentials = Security(security)
                       ) -> dict:

    """
    The remove_image function is used to remove an image from the database.
    The function takes in a required image_id parameter, which is the id of the image that will be removed.
    The function also takes in a db parameter, which is used to access and modify data within our database.
    This db parameter uses Depends(get_db) as its default value, meaning it will use get_db() as its default value if no other value for this paramter is provided when calling this function.


    :param image_id: int: Specify the id of the image to be removed
    :param db: Session: Pass the database connection to the function
    :param current_user: dict: Get the current user information
    :param credentials: HTTPAuthorizationCredentials: Authenticate the user
    :return: A dict with a key &quot;message&quot; and value of the message
    :doc-author: Trelent
    """
    message = await repository_images.remove_image(image_id, current_user, db)
    return message


@router.put(
            '/{image_id}',
            description=f'Update image.\nNo more than {settings.limit_crit} requests per minute.',
            dependencies=[Depends(RateLimiter(times=settings.limit_crit, seconds=settings.limit_crit_timer))
                          ],
            response_model=ImageResponse
            )
async def update_image(
                       body: ImageModel,
                       image_id: int = Path(ge=1),
                       db: Session = Depends(get_db),
                       current_user: dict = Depends(AuthUser.get_current_user),
                       credentials: HTTPAuthorizationCredentials = Security(security)
                       ) -> Image:
    """
    The update_image function updates an image in the database.

    :param body: ImageModel: Validate the data sent in the request body
    :param image_id: int: Get the image id from the path
    :param db: Session: Get the database session
    :param current_user: dict: Get the current user information
    :param credentials: HTTPAuthorizationCredentials: Check if the user is authenticated
    :return: The updated image
    :doc-author: Trelent
    """
    image = await repository_images.update_image(image_id, body, current_user, db, settings.tags_limit)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)

    return image


@router.get(
            '/search_bytag/{tag_name}',
            description=f'Get images by tag.\nNo more than {settings.limit_warn} requests per minute.',
            dependencies=[
                          Depends(allowed_all_roles_access),
                          Depends(RateLimiter(times=settings.limit_warn, seconds=settings.limit_crit_timer))
                          ],
            response_model=List[ImageResponse]
            )
async def get_image_by_tag_name(
                                tag_name: str,
                                sort_direction: SortDirection,
                                db: Session = Depends(get_db),
                                current_user: dict = Depends(AuthUser.get_current_user),
                                credentials: HTTPAuthorizationCredentials = Security(security)
                                ) -> List[Image]:
    """
    The get_image_by_tag_name function returns a list of images that have the tag name specified in the request.
    The function takes three parameters:
    - tag_name: The name of the tag to search for. This is a required parameter and must be passed as part of
    the URL path (e.g., /images/tags/{tag_name}). It is also validated by FastAPI to ensure it meets
    certain criteria, such as being non-empty and not exceeding 255 characters in length.

    :param tag_name: str: Specify the tag name to search for
    :param sort_direction: SortDirection: Sort the images by date
    :param db: Session: Get the database session
    :param current_user: dict: Get the current user from the database
    :param credentials: HTTPAuthorizationCredentials: Validate the token
    :return: A list of images
    :doc-author: Trelent
    """
    tag = await repository_tags.get_tag_by_name(tag_name, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_TAG_NOT_FOUND)

    images = await repository_images.get_images_by_tag(tag, sort_direction, db)
    if images is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)

    return images


@router.get(
            '/search_byuser/{user_id}',
            description=f'Get images by user_id.\nNo more than {settings.limit_warn} requests per minute.',
            dependencies=[
                          Depends(allowed_admin_moderator),
                          Depends(RateLimiter(times=settings.limit_warn, seconds=settings.limit_crit_timer))
                          ],
            response_model=List[ImageResponse]
            )
async def get_image_by_user(
                            user_id: int,
                            sort_direction: SortDirection,
                            db: Session = Depends(get_db),
                            current_user: dict = Depends(AuthUser.get_current_user),
                            credentials: HTTPAuthorizationCredentials = Security(security)
                            ) -> List[Image]:
    """
    The get_image_by_user function returns a list of images that are associated with the user_id provided.
    The function will return an HTTP 404 error if no image is found or if the user_id does not exist.

    :param user_id: int: Get the user id from the url
    :param sort_direction: SortDirection: Sort the images by date in ascending or descending order
    :param db: Session: Get the database session
    :param current_user: dict: Get the current user's id
    :param credentials: HTTPAuthorizationCredentials: Authenticate the user
    :return: A list of images
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_USER_NOT_FOUND)

    images = await repository_images.get_images_by_user(user_id, sort_direction, db)
    if not any(images):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)

    return images


add_pagination(router)
