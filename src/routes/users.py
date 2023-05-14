from fastapi import APIRouter, Depends, UploadFile, File  # status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.schemas import UserDb
from src.services.auth import AuthUser
from src.services.images import CloudImage  # cloud_image


router = APIRouter(prefix='/users', tags=['users'])
authuser = AuthUser()


@router.get('/me', response_model=UserDb)  # /me/  ?
async def read_users_me(current_user: User = Depends(authuser.get_current_user)) -> User:
    return current_user


# TODO profile foe all users =>
@router.get('/about_{user_id}', response_model=UserDb)
async def read_about_user(
                          user_id: int,
                          current_user: User = Depends(authuser.get_current_user), 
                          db: Session = Depends(get_db)
                          ) -> User:
    # ... add number of uploaded images, etc ...
    user = repository_users.get_user_by_id(user_id, db)
    user.number_images = repository_users.get_number_of_images_per_user(user.email, db)
    
    return user


@router.put(f'/{authuser.get_current_user.username}', response_model=UserDb)
async def update_user_profile(
                              current_user: User = Depends(authuser.get_current_user), 
                              db: Session = Depends(get_db)
                              ) -> User:
    
    ...
    
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(
                             file: UploadFile = File(), 
                             current_user: User = Depends(authuser.get_current_user),
                             db: Session = Depends(get_db)
                             ) -> User:
    
    src_url = CloudImage.avatar_upload(file.file, current_user.email)

    user = await repository_users.update_avatar(current_user.email, src_url, db)

    return user
