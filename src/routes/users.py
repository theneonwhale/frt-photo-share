from fastapi import APIRouter, Depends, HTTPException, Security, status, UploadFile, File
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.conf.messages import MSC404_USER_NOT_FOUND
from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.schemas import UserDb, UserResponseFull, UserType, UserBase
from src.services.auth import authuser, security
from src.services.images import CloudImage


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSC404_USER_NOT_FOUND)
    
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSC404_USER_NOT_FOUND)
    
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSC404_USER_NOT_FOUND)

    return user
