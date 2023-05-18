from fastapi import APIRouter, Depends, HTTPException, Security, status, UploadFile, File
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.conf import messages
from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.shemas.users import UserBase, UserType, UserDb, UserResponseFull
from src.services.auth import authuser, security

from src.services.images import CloudImage 
from src.services.roles import allowed_operation_delete


router = APIRouter(prefix='/users', tags=['users'])


@router.get('/me', response_model=UserDb, name='Get user info')
async def read_users_me(
                        current_user: dict = Depends(authuser.get_current_user),
                        credentials: HTTPAuthorizationCredentials = Security(security),
                        db: Session = Depends(get_db)
                        ) -> User:
    return await repository_users.get_user_by_id(current_user.get('id'), db)


@router.get('/{user_id}', response_model=UserResponseFull, name='Get user info by id')
async def read_user_by_id(
                          user_id: int,
                          current_user: dict = Depends(authuser.get_current_user),
                          credentials: HTTPAuthorizationCredentials = Security(security),
                          db: Session = Depends(get_db)
                          ) -> dict:
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_USER_NOT_FOUND)

    user.number_images = await repository_users.get_number_of_images_per_user(user.email, db)
    return user


@router.put('/{user_id}', response_model=UserDb)
async def update_user_profile(
                              user_id: int,
                              body: UserType,
                              current_user: dict = Depends(authuser.get_current_user),
                              credentials: HTTPAuthorizationCredentials = Security(security), 
                              db: Session = Depends(get_db)
                              ) -> User:
    user = await repository_users.update_user_profile(user_id, current_user, body, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_USER_NOT_FOUND)
    
    return user


@router.put('/me/{user_id}', response_model=UserDb)
async def update_your_profile(
                              user_id: int,
                              body: UserBase,
                              current_user: dict = Depends(authuser.get_current_user), 
                              credentials: HTTPAuthorizationCredentials = Security(security),
                              db: Session = Depends(get_db)
                              ) -> User:
    user = await repository_users.update_your_profile(current_user.get('email'), body, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_USER_NOT_FOUND)
    
    return user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(
                             file: UploadFile = File(), 
                             current_user: dict = Depends(authuser.get_current_user),
                             credentials: HTTPAuthorizationCredentials = Security(security),
                             db: Session = Depends(get_db)
                             ) -> User:
    src_url = CloudImage.avatar_upload(file.file, current_user.get('email'))

    user = await repository_users.update_avatar(current_user.get('email'), src_url, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_USER_NOT_FOUND)

    return user


@router.patch(
              '/ban_user', response_model=UserDb,
              dependencies=[Depends(allowed_operation_delete)],
              description='Ban/unBan user'
              )
async def bun_user(
                   user_id: int,
                   active_status: bool,
                   current_user: dict = Depends(authuser.get_current_user),
                   db: Session = Depends(get_db)
                   ):
    user = await repository_users.ban_user(user_id, active_status, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.MSC403_USER_BANNED)
    
    await authuser.clear_user_cash(user.email)

    return user
