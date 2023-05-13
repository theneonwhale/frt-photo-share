from fastapi import APIRouter, Depends, UploadFile, File  # status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.schemas import UserDb
from src.services.auth import auth_service
from src.services.images import CloudImage  # cloud_image


router = APIRouter(prefix='/users', tags=['users'])


@router.get('/me/', response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)) -> User:
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(
                             file: UploadFile = File(), 
                             current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)
                             ) -> User:
    
    src_url = CloudImage.avatar_upload(file.file, current_user.email)

    user = await repository_users.update_avatar(current_user.email, src_url, db)

    return user