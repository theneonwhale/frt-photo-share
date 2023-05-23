from typing import Optional, List

from fastapi import APIRouter, Depends, Path, Security, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.conf import messages
from src.conf.config import settings
from src.database.db import get_db
from src.database.models import Rating
from src.schemas.images import RatingResponse, RatingModel
from src.schemas.users import MessageResponse
from src.services.auth import AuthUser, security
from src.services.roles import allowed_all_roles_access, allowed_admin_moderator

from src.repository import images as repository_images
from src.repository import ratings as repository_ratings

router = APIRouter(prefix='/rating', tags=['ratings'])


@router.post(
             '/{image_id}',
             description=f'Add rating.\nCan rate for an image only once.',
             dependencies=[
                           Depends(allowed_all_roles_access),
                           Depends(RateLimiter(times=settings.limit_crit, seconds=settings.limit_crit_timer))
                           ],
             response_model=RatingResponse
             )
async def add_rating(
                     body: RatingModel,
                     image_id: int = Path(ge=1),
                     db: Session = Depends(get_db),
                     current_user: dict = Depends(AuthUser.get_current_user),
                     credentials: HTTPAuthorizationCredentials = Security(security)
                     ) -> RatingResponse:
    image = await repository_images.get_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)

    existing_rating = db.query(Rating).filter_by(user_id=current_user['id'], image_id=image_id).first()
    if existing_rating:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.MSC400_ALREADY_RATED)

    if image.user_id == current_user['id']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.OWN_RATING)

    rating = await repository_ratings.add_rating(body, image_id, current_user, db)
    return rating


@router.get(
            '/{image_id}',
            description=f'Get all ratings for image.\nNo more than {settings.limit_crit} requests per minute.',
            dependencies=[
                          Depends(allowed_admin_moderator),
                          Depends(RateLimiter(times=settings.limit_crit, seconds=settings.limit_crit_timer))
                          ],
            response_model=List[RatingResponse]
            )
async def get_ratings(
                      image_id: int = Path(ge=1),
                      db: Session = Depends(get_db),
                      current_user: dict = Depends(AuthUser.get_current_user),
                      credentials: HTTPAuthorizationCredentials = Security(security)
                      ) -> List[RatingResponse]:
    image = await repository_images.get_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)

    ratings = await repository_ratings.get_ratings(image_id, db)

    return ratings


@router.delete(
               '/{rating_id}',
               description=f'Delete rating.\nNo more than {settings.limit_crit} requests per minute.',
               dependencies=[
                             Depends(allowed_admin_moderator),
                             Depends(RateLimiter(times=settings.limit_crit, seconds=settings.limit_crit_timer))
                             ],
               response_model=MessageResponse
               )
async def remove_rating(
                        rating_id: int = Path(ge=1),
                        db: Session = Depends(get_db),
                        current_user: dict = Depends(AuthUser.get_current_user),
                        credentials: HTTPAuthorizationCredentials = Security(security)
                        ) -> dict:
    message = await repository_ratings.remove_rating(rating_id, current_user, db)

    return message
