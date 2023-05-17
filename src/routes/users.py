from fastapi import APIRouter, Depends, File, HTTPException, Security, status, UploadFile, File
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.conf.messages import *
from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.schemas import UserDb, UserModel, UserResponse, UserResponseFull, UserType
from src.services.auth import authuser, security
from src.services.images import CloudImage  # cloud_image
from src.services.roles import allowed_operation_delete

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/me', response_model=UserDb)  # /me/  ?
async def read_users_me(
                        current_user: dict = Depends(authuser.get_current_user),
                        credentials: HTTPAuthorizationCredentials = Security(security),
                        db: Session = Depends(get_db)
                        ) -> User:
    return await repository_users.get_user_by_id(current_user.get('id'), db)


@router.get('/about_{user_id}', response_model=UserResponseFull)
async def read_about_user(
                          user_id: int,
                          current_user: dict = Depends(authuser.get_current_user), 
                          credentials: HTTPAuthorizationCredentials = Security(security),
                          db: Session = Depends(get_db)
                          ) -> dict:
    # ... add number of uploaded images, etc ...
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSC404_USER_NOT_FOUND)
    
    about_user = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at,
            'avatar': user.avatar,
            'roles': user.roles,
            'status_active': user.status_active,
            'number_images': await repository_users.get_number_of_images_per_user(user.email, db),
            }
    
    return about_user


@router.put('/{username}', response_model=UserDb)  # username = email !
async def update_user_profile(
                              username: str,  # !
                              body: UserType,
                              current_user: dict = Depends(authuser.get_current_user),
                              credentials: HTTPAuthorizationCredentials = Security(security), 
                              db: Session = Depends(get_db)
                              ) -> User:
    
    current_user = await repository_users.update_user(username, body, db)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSC404_USER_NOT_FOUND)
    
    return current_user


@router.put('/me/{username}', response_model=UserDb)
async def update_your_profile(
                              body: UserType,
                              current_user: dict = Depends(authuser.get_current_user), 
                              credentials: HTTPAuthorizationCredentials = Security(security),
                              db: Session = Depends(get_db)
                              ) -> User:
    
    current_user = await repository_users.update_user(current_user.get('email'), body, db)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSC404_USER_NOT_FOUND)
    
    return current_user


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSC404_USER_NOT_FOUND)

    return user


@router.patch('/ban_user', response_model=UserDb,
              dependencies=[Depends(allowed_operation_delete)],
              description='Ban/unBan user')
async def bun_user(
        user_id: int,
        active_status: bool,
        current_user: dict = Depends(authuser.get_current_user),
        db: Session = Depends(get_db)
):
    user = await repository_users.bun_user(user_id, active_status, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=MSC403_USER_BANNED)
    await authuser.clear_user_cash(user.email)

    return user
