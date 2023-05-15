import io
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Path, Security, status, UploadFile 
from fastapi_limiter.depends import RateLimiter
from fastapi_pagination import add_pagination, Page, Params  # poetry add fastapi-pagination==0.11.4
from fastapi.security import HTTPAuthorizationCredentials
from starlette.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.conf.messages import *
from src.database.db import get_db
from src.database.models import Image, TransformationsType
from src.repository import images as repository_images
from src.schemas import ImageModel, ImageResponse, CommentModel
from src.services.auth import authuser, security
from src.services.images import CloudImage  #, cloud_image
from src.services.roles import allowed_all_roles_access, allowed_operation_delete, allowed_operation_update


router = APIRouter(prefix='/images')  # tags=['images']


# https://pypi.org/project/python-redis-rate-limit/
@router.get(
            '/', 
            description=f'Get images.\nNo more than {settings.limit_crit} requests per minute.',
            dependencies=[
                          Depends(allowed_all_roles_access),
                          Depends(RateLimiter(times=settings.limit_crit, seconds=60))
                          ],
            response_model=Page, 
            tags=['all_images']
            )
async def get_images(
                       db: Session = Depends(get_db),
                       current_user: dict = Depends(authuser.get_current_user),
                       credentials: HTTPAuthorizationCredentials = Security(security),
                       pagination_params: Params = Depends()
                       ) -> Page:

    images = await repository_images.get_images(current_user, db, pagination_params)  # db, pagination_params

    return images


@router.post(
            '/transformation/{image_id}',
            description=f'Transform image.\nNo more than {settings.limit_crit} requests per minute.',
            dependencies=[
                           Depends(allowed_all_roles_access),
                           Depends(RateLimiter(times=settings.limit_crit, seconds=60))
                           ],
            response_model=ImageResponse, 
            tags=['image']
            )
async def transform_image(
                        type: TransformationsType,
                        image_id: int = Path(ge=1),
                        db: Session = Depends(get_db),
                        current_user: dict = Depends(authuser.get_current_user),
                        credentials: HTTPAuthorizationCredentials = Security(security)
                        ) -> Optional[Image]:
    image = await repository_images.get_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSC404_IMAGE_NOT_FOUND)
    if image.user_id != current_user['id']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=MSC400_BAD_REQUEST)

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
                           Depends(RateLimiter(times=settings.limit_crit, seconds=60))
                           ],
            tags=['image']
            )
async def image_qrcode(
                        image_id: int = Path(ge=1),
                        db: Session = Depends(get_db),
                        current_user: dict = Depends(authuser.get_current_user),
                        ):
    image = await repository_images.get_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSC404_IMAGE_NOT_FOUND)

    qr_code = CloudImage.get_qrcode(image)
    output = io.BytesIO()
    qr_code.save(output)
    output.seek(0)

    return StreamingResponse(output, media_type="image/png")



@router.get(
            '/{image_id}',
            description=f'Get image.\nNo more than {settings.limit_warn} requests per minute.',
            dependencies=[
                          Depends(allowed_all_roles_access),
                          Depends(RateLimiter(times=settings.limit_warn, seconds=60))
                          ],
            response_model=ImageResponse, 
            tags=['image']
            )
async def get_image(
                    image_id: int = Path(ge=1),
                    db: Session = Depends(get_db),
                    current_user: dict = Depends(authuser.get_current_user),
                    credentials: HTTPAuthorizationCredentials = Security(security)
                    ) -> Optional[Image]:

    image = await repository_images.get_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSC404_IMAGE_NOT_FOUND)

    return image


@router.post(
            '/',
            description=f'Create image.\nNo more than {settings.limit_warn} requests per minute.',
            dependencies=[
                          Depends(allowed_all_roles_access),
                          Depends(RateLimiter(times=settings.limit_warn, seconds=60))
                          ],
            response_model=ImageResponse, 
            tags=['image']
            )
async def create_image(
                       description: str = '-',
                       tags: str = '',
                       file: UploadFile = File(),
                       db: Session = Depends(get_db),
                       current_user: dict = Depends(authuser.get_current_user),
                       credentials: HTTPAuthorizationCredentials = Security(security)
                       ) -> Image:
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
                             # Depends(allowed_operation_delete),
                             Depends(RateLimiter(times=settings.limit_warn, seconds=60))
                             ],
               response_model=ImageResponse, 
               tags=['image']
               )
async def remove_image(
                       image_id: int = Path(ge=1),
                       db: Session = Depends(get_db),
                       current_user: dict = Depends(authuser.get_current_user),
                       credentials: HTTPAuthorizationCredentials = Security(security)
                       ) -> Optional[Image]:

    image = await repository_images.remove_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSC404_IMAGE_NOT_FOUND)
    
    return image


# EDIT image...
@router.put(
            '/{image_id}', 
            description=f'Update image.\nNo more than {settings.limit_crit} requests per minute.',
            dependencies=[
                          # Depends(allowed_operation_update),
                          Depends(RateLimiter(times=settings.limit_crit, seconds=60))
                          ],
            response_model=ImageResponse, 
            tags=['image']
            )
async def update_image(
                       body: ImageModel,
                       image_id: int = Path(ge=1), 
                       db: Session = Depends(get_db),
                       current_user: dict = Depends(authuser.get_current_user),
                       credentials: HTTPAuthorizationCredentials = Security(security)
                       ) -> Image:  

    image = await repository_images.update_image(image_id, body, current_user, db, settings.tags_limit)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSC404_IMAGE_NOT_FOUND)

    return image




# https://github.com/uriyyo/fastapi-pagination
add_pagination(router)