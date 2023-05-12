from fastapi import Depends, HTTPException, status, APIRouter, Security, BackgroundTasks, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, Token, RequestEmail
from src.repository import users as repository_users
from src.services.auth import AuthPassword, AuthToken, AuthUser
from src.services.email import send_email
from src.conf.messages import *

router = APIRouter(prefix="/auth", tags=['auth'])
security = HTTPBearer()
authpassword = AuthPassword()
authtoken = AuthToken()
authuser = AuthUser()


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": EMAIL_ERROR_CONFIRMED}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": EMAIL_INFO_CONFIRMED}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = await authtoken.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=MSC400_BAD_REQUEST)
    if user.email_confirm:
        return {"message": EMAIL_ERROR_CONFIRMED}
    await repository_users.confirmed_email(email, db)
    return {"message": EMAIL_INFO_CONFIRM}
