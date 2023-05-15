from fastapi import APIRouter, Depends, File, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from src.conf.messages import MSC404_USER_NOT_FOUND
from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.schemas import UserDb, UserModel
from src.services.auth import authuser
from src.services.images import CloudImage  # cloud_image


router = APIRouter(prefix='/users', tags=['users'])


@router.get('/me', response_model=UserDb)  # /me/  ?
async def read_users_me(current_user: User = Depends(authuser.get_current_user)) -> User:
    return current_user


@router.get('/about_{user_id}', response_model=UserDb)
async def read_about_user(
                          user_id: int,
                          current_user: User = Depends(authuser.get_current_user), 
                          db: Session = Depends(get_db)
                          ) -> dict:
    # ... add number of uploaded images, etc ...
    user = repository_users.get_user_by_id(user_id, db)
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
            'number_images': repository_users.get_number_of_images_per_user(user.email, db),
            }
    
    return about_user


@router.put(f'''/{authuser.get_current_user.get('username')}''', response_model=UserDb)
async def update_user_profile(
                              body: UserModel,
                              current_user: User = Depends(authuser.get_current_user), 
                              db: Session = Depends(get_db)
                              ) -> User:
    
    current_user = repository_users.update_user(current_user.get('email'), body, db)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSC404_USER_NOT_FOUND)
    
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(
                             file: UploadFile = File(), 
                             current_user: User = Depends(authuser.get_current_user),
                             db: Session = Depends(get_db)
                             ) -> User:
    
    src_url = CloudImage.avatar_upload(file.file, current_user.get('email'))

    user = await repository_users.update_avatar(current_user.get('email'), src_url, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSC404_USER_NOT_FOUND)

    return user
