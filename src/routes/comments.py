from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Path, Security, status
from fastapi_limiter.depends import RateLimiter
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.conf import messages
from src.database.db import get_db
from src.database.models import Comment
from src.repository import images as repository_images
from src.repository import comments as repository_comments
from src.schemas import CommentModel, CommentResponse
from src.services.auth import authuser, security
from src.services.roles import allowed_all_roles_access, allowed_operation_delete, allowed_operation_update


router = APIRouter(prefix='/comment', tags=['comments'])


@router.get(
    '/{image_id}',
    description=f'Get all comments on image.\nNo more than {settings.limit_crit} requests per minute.',
    dependencies=[
        Depends(allowed_all_roles_access),
        Depends(RateLimiter(times=settings.limit_crit, seconds=settings.limit_crit_timer))
    ],
    response_model=List[CommentResponse],
)
async def get_comments_by_image_id(
        image_id: int = Path(ge=1),
        db: Session = Depends(get_db),
        current_user: dict = Depends(authuser.get_current_user),
        credentials: HTTPAuthorizationCredentials = Security(security)
        ) -> List[Comment]:
    image = await repository_images.get_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)

    return await repository_comments.get_comments(image_id, db)

@router.post(
    '/{image_id}',
    description=f'Add comment.\nNo more than {settings.limit_crit} requests per minute.',
    dependencies=[
        Depends(allowed_all_roles_access),
        Depends(RateLimiter(times=settings.limit_crit, seconds=settings.limit_crit_timer))
    ],
    response_model=CommentResponse,
)
async def add_comment(
        body: CommentModel,
        image_id: int = Path(ge=1),
        db: Session = Depends(get_db),
        current_user: dict = Depends(authuser.get_current_user),
        credentials: HTTPAuthorizationCredentials = Security(security)
) -> Optional[Comment]:
    image = await repository_images.get_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)
    comment = await repository_comments.add_comment(body, image_id, current_user, db)
    return comment


@router.put(
            '/{comment_id}',
            description=f'Update comment.\nNo more than {settings.limit_crit} requests per minute.',
            dependencies=[
                Depends(allowed_operation_update),
                Depends(RateLimiter(times=settings.limit_crit, seconds=settings.limit_crit_timer))
            ],
            response_model=CommentResponse,
             )
async def update_comment(
                         body: CommentModel,
                         comment_id: int = Path(ge=1),
                         db: Session = Depends(get_db),
                         current_user: dict = Depends(authuser.get_current_user),
                         credentials: HTTPAuthorizationCredentials = Security(security)
                         ) -> Comment:
    comment = await repository_comments.update_comment(comment_id, body, current_user, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_COMMENT_NOT_FOUND)

    return comment


@router.delete(
               '/{comment_id}',
               description=f'Delete comment.\nNo more than {settings.limit_crit} requests per minute.',
               dependencies=[
                             Depends(allowed_operation_delete),
                             Depends(RateLimiter(times=settings.limit_crit, seconds=settings.limit_crit_timer))
                             ],
                response_model=CommentResponse,
                )
async def remove_comment(
                         comment_id: int = Path(ge=1),
                         db: Session = Depends(get_db),
                         current_user: dict = Depends(authuser.get_current_user),
                         credentials: HTTPAuthorizationCredentials = Security(security)
                         ) -> Optional[Comment]:
    comment = await repository_comments.remove_comment(comment_id, current_user, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_COMMENT_NOT_FOUND)

    return comment
