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
from src.schemas.images import CommentModel, CommentResponse
from src.services.auth import AuthUser, security
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
        current_user: dict = Depends(AuthUser.get_current_user),
        credentials: HTTPAuthorizationCredentials = Security(security)
        ) -> List[Comment]:

    """
    The get_comments_by_image_id function returns a list of comments for the image with the given id.

    :param image_id: int: Specify the image id of the comment to be created
    :param db: Session: Get the database session
    :param current_user: dict: Get the current user information
    :param credentials: HTTPAuthorizationCredentials: Validate the token
    :return: A list of comments
    :doc-author: Trelent
    """
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
        current_user: dict = Depends(AuthUser.get_current_user),
        credentials: HTTPAuthorizationCredentials = Security(security)
) -> Optional[Comment]:

    """
    The add_comment function adds a comment to an image.
    The function takes in the following parameters:
    body: CommentModel - A model containing the information for a new comment.
    image_id: int - The id of the image that is being commented on. This parameter is required and must be greater than or equal to 1 (Path(ge=0)).
    db: Session = Depends(get_db) - A database session object used for querying and modifying data in our database (Depends).
    This parameter is optional, but if it isn't provided, then one will be created using

    :param body: CommentModel: Validate the request body
    :param image_id: int: Get the image from the database
    :param db: Session: Access the database
    :param current_user: dict: Get the current user from the database
    :param credentials: HTTPAuthorizationCredentials: Authenticate the user
    :return: A comment object
    :doc-author: Trelent
    """
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
                         current_user: dict = Depends(AuthUser.get_current_user),
                         credentials: HTTPAuthorizationCredentials = Security(security)
                         ) -> Comment:

    """
    The update_comment function updates a comment in the database.
    The function takes an id of a comment, and returns the updated comment.
    If no such id exists, it raises an HTTPException with status code 404.

    :param body: CommentModel: Get the body of the comment
    :param comment_id: int: Get the comment id from the url
    :param db: Session: Get the database session
    :param current_user: dict: Get the user who is logged in
    :param credentials: HTTPAuthorizationCredentials: Check if the user is authenticated
    :return: The updated comment
    :doc-author: Trelent
    """
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
                         current_user: dict = Depends(AuthUser.get_current_user),
                         credentials: HTTPAuthorizationCredentials = Security(security)
                         ) -> Optional[Comment]:

    """
    The remove_comment function removes a comment from the database.

    :param comment_id: int: Get the comment id from the url
    :param db: Session: Access the database
    :param current_user: dict: Get the current user
    :param credentials: HTTPAuthorizationCredentials: Validate the user's token
    :return: A comment object
    :doc-author: Trelent
    """
    comment = await repository_comments.remove_comment(comment_id, current_user, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_COMMENT_NOT_FOUND)

    return comment
