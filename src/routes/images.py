from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi_limiter.depends import RateLimiter
from fastapi_pagination import add_pagination, Page, Params  # poetry add fastapi-pagination
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.conf.messages import MSC404_IMAGE_NOT_FOUND
from src.database.db import get_db
from src.database.models import Image, User
from src.repository import images as repository_images
from src.schemas import ImageModel, ImageResponse
from src.services.auth import AuthUser


router = APIRouter(prefix='/images')  # tags=['images']
authuser = AuthUser()

# https://pypi.org/project/python-redis-rate-limit/
@router.get(
            '/', 
            description=f'No more than {settings.limit_crit} requests per minute.',
            dependencies=[Depends(RateLimiter(times=settings.limit_crit, seconds=60))],
            response_model=Page, tags=['all_images']
            )
async def get_images(
                       db: Session = Depends(get_db), 
                       current_user: User = Depends(authuser.get_current_user),
                       pagination_params: Params = Depends()
                       ) -> Page:
 
    images = await repository_images.get_images(current_user, db, pagination_params)  # db, pagination_params

    return images


@router.get(
            '/{image_id}', 
            description=f'No more than {settings.limit_warn} requests per minute.',
            dependencies=[Depends(RateLimiter(times=settings.limit_warn, seconds=60))],
            response_model=ImageResponse, tags=['image']
            )
async def get_image(
                    image_id: int = Path(ge=1),
                    db: Session = Depends(get_db),
                    current_user: User = Depends(authuser.get_current_user)
                    ) -> Optional[Image]:

    image = await repository_images.get_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSC404_IMAGE_NOT_FOUND)
    
    return image


@router.delete(
               '/{image_id}', 
               description=f'No more than {settings.limit_crit} requests per minute',
               dependencies=[Depends(RateLimiter(times=settings.limit_warn, seconds=60))],
               response_model=ImageResponse, tags=['image']
               )
async def remove_image(
                       image_id: int = Path(ge=1),
                       db: Session = Depends(get_db),
                       current_user: User = Depends(authuser.get_current_user)
                       ) -> Optional[Image]:

    image = await repository_images.remove_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSC404_IMAGE_NOT_FOUND)
    
    return image


# https://github.com/uriyyo/fastapi-pagination
add_pagination(router)
