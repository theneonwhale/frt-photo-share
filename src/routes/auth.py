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


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             description='Create new user')
async def sign_up(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    check_user = await repository_users.get_user_by_email(body.email, db)
    if check_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=MSC409_CONFLICT)

    body.password = authpassword.get_hash_password(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=Token)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=MSC401_EMAIL)
    if not authpassword.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=MSC401_PASSWORD)
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"check {user.email} to Confirm account")

    access_token = await authtoken.create_access_token(data={"sub": user.email})
    refresh_token = await authtoken.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh_token", response_model=Token)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = await authtoken.refresh_token_email(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=MSC401_TOKEN)

    access_token = await authtoken.create_access_token(data={"sub": email})
    refresh_token = await authtoken.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


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
    print('======'*8)
    email = await authtoken.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=MSC400_BAD_REQUEST)
    if user.confirmed:
        return {"message": EMAIL_ERROR_CONFIRMED}
    await repository_users.confirmed_email(email, db)
    return {"message": EMAIL_INFO_CONFIRM}



# http://127.0.0.1:8000/api/auth/confirmed_email/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1bmZlaXJAZ21haWwuY29tIiwiaWF0IjoxNjgzODk1Mzc2LCJleHAiOjE2ODM4OTg5NzZ9.JgdgICLhyGPZyxn2fcq114Spyo0VN5rToCnNVh7fzYA