from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Security, status, UploadFile, File
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.conf import messages
from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.schemas.users import UserDb, UserResponseFull, UserType, UserBase
from src.services.auth import AuthUser, security

from src.services.images import CloudImage
from src.services.roles import allowed_admin_moderator


router = APIRouter(prefix='/users', tags=['users'])


@router.get('/me', response_model=UserDb, name='Get user info')
async def read_users_me(
                        current_user: dict = Depends(AuthUser.get_current_user),
                        credentials: HTTPAuthorizationCredentials = Security(security),
                        db: Session = Depends(get_db)
                        ) -> User:
    """
    The read_users_me function is a GET request that returns the current user's information.
    The function requires an authorization header with a valid JWT token to be passed in order for it to work.

    :param current_user: dict: Get the current user from the database
    :param credentials: HTTPAuthorizationCredentials: Validate the security scheme
    :param db: Session: Pass the database session to the repository layer
    :return: The user object of the currently logged in user
    :doc-author: Trelent
    """
    return await repository_users.get_user_by_id(current_user.get('id'), db)


@router.get('/{user_id}', response_model=UserResponseFull, name='Get user info by id')
async def read_user_by_id(
                          user_id: int,
                          current_user: dict = Depends(AuthUser.get_current_user),
                          credentials: HTTPAuthorizationCredentials = Security(security),
                          db: Session = Depends(get_db)
                          ) -> dict:
    """
    The read_user_by_id function reads a user by its id.

    :param user_id: int: Get the user id from the url
    :param current_user: dict: Get the current user
    :param credentials: HTTPAuthorizationCredentials: Validate the token in the header of the request
    :param db: Session: Pass the database session to the repository layer
    :return: A dictionary with the user information
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_USER_NOT_FOUND)

    user.number_images = await repository_users.get_number_of_images_per_user(user.email, db)
    return user


@router.put('/{user_id}', response_model=UserDb)
async def update_user_profile(
                              user_id: int,
                              body: UserType,
                              current_user: dict = Depends(AuthUser.get_current_user),
                              credentials: HTTPAuthorizationCredentials = Security(security),
                              db: Session = Depends(get_db)
                              ) -> User:

    """
    The update_user_profile function updates the user profile.
        Args:
            user_id (int): The id of the user to update.
            body (UserType): The updated information for the specified user.

    :param user_id: int: Identify the user to be deleted
    :param body: UserType: Validate the data sent by the user
    :param current_user: dict: Get the current user
    :param credentials: HTTPAuthorizationCredentials: Validate the token
    :param db: Session: Access the database
    :return: A user object
    :doc-author: Trelent
    """
    user = await repository_users.update_user_profile(user_id, current_user, body, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_USER_NOT_FOUND)

    return user


@router.put('/me/{user_id}', response_model=UserDb)
async def update_your_profile(
                              user_id: int,
                              body: Optional[UserBase] = None,
                              current_user: dict = Depends(AuthUser.get_current_user),
                              credentials: HTTPAuthorizationCredentials = Security(security),
                              db: Session = Depends(get_db)
                              ) -> User:
    """
    The update_your_profile function updates the current user's profile.
        Args:
            user_id (int): The id of the user to update.
            body (UserBase): The updated information for the User object.

    :param user_id: int: Identify the user
    :param body: UserBase: Get the data from the request body
    :param current_user: dict: Get the current user's email
    :param credentials: HTTPAuthorizationCredentials: Check the token
    :param db: Session: Access the database
    :return: The user object
    :doc-author: Trelent
    """
    user = await repository_users.update_your_profile(current_user.get('email'), body, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_USER_NOT_FOUND)

    return user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(
                             file: UploadFile = File(),
                             current_user: dict = Depends(AuthUser.get_current_user),
                             credentials: HTTPAuthorizationCredentials = Security(security),
                             db: Session = Depends(get_db)
                             ) -> User:
    """
    The update_avatar_user function updates the avatar of a user.
        The function takes in an UploadFile object (picture), which is a file that has been uploaded to the server.
        It also takes in current_user and credentials as dependencies, which are used for authentication purposes.
        Finally it takes in db as a dependency, which is used to access the database.

    :param file: UploadFile: Upload the file to the cloud
    :param current_user: dict: Get the current user's email
    :param credentials: HTTPAuthorizationCredentials: Validate the token
    :param db: Session: Access the database
    :return: The user data
    :doc-author: Trelent
    """
    src_url = CloudImage.avatar_upload(file.file, current_user.get('email'))

    user = await repository_users.update_avatar(current_user.get('email'), src_url, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_USER_NOT_FOUND)

    return user


@router.patch(
              '/ban_user/{user_id}/{active_status}', response_model=UserDb,
              dependencies=[Depends(allowed_admin_moderator)],
              description='Ban/unban user'
              )
async def ban_user(
                   user_id: int,
                   active_status: bool,
                   current_user: dict = Depends(AuthUser.get_current_user),
                   credentials: HTTPAuthorizationCredentials = Security(security),
                   db: Session = Depends(get_db)
                   ) -> User:
    """
    The ban_user function is used to ban a user from the system.

    :param user_id: int: Identify the user to be banned
    :param active_status: bool: Set the user's status to active or inactive
    :param current_user: dict: Get the current user from the authuser class
    :param db: Session: Access the database
    :return: The banned user object
    :doc-author: Trelent
    """
    user: Optional[User] = await repository_users.ban_user(user_id, active_status, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_USER_NOT_FOUND)

    await AuthUser.clear_user_cash(user.email)

    return user
