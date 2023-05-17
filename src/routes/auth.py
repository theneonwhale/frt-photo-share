from fastapi import (
    Depends,
    HTTPException,
    status,
    APIRouter,
    Security,
    BackgroundTasks,
    Request
)
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from starlette.templating import _TemplateResponse
from sqlalchemy.orm import Session

from src.conf.messages import *
from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.schemas import (
                         MessageRequest,
                         PasswordRecovery,
                         RequestEmail,
                         Token,
                         UserModel,
                         UserResponse,
                        )
from src.services.auth import authpassword, authtoken, authuser, security
from src.services.email import send_email, send_new_password, send_reset_password


router = APIRouter(prefix='/auth', tags=['auth'])
templates = Jinja2Templates(directory='src/services/templates')


@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             description='Create new user')
async def sign_up(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)) -> User:
    check_user = await repository_users.get_user_by_email(body.email, db)
    if check_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=MSC409_CONFLICT)

    body.password = authpassword.get_hash_password(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))

    return new_user


@router.post('/login', response_model=Token)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict:
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=MSC401_EMAIL)

    if not authpassword.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=MSC401_PASSWORD)

    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=MSC401_EMAIL_UNKNOWN)

    access_token = await authtoken.create_access_token(data={'sub': user.email})
    refresh_token = await authtoken.create_refresh_token(data={'sub': user.email})
    await repository_users.update_token(user, refresh_token, db)

    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': TOKEN_TYPE}


@router.get("/logout", response_class=HTMLResponse)
async def logout(
           credentials: HTTPAuthorizationCredentials = Security(security),
           current_user: dict = Depends(authuser.logout_user)
           ) -> RedirectResponse:
    resp = RedirectResponse(url="/login", status_code=status.HTTP_205_RESET_CONTENT)

    return resp


@router.post('/refresh_token', response_model=Token)
async def refresh_token(
                        credentials: HTTPAuthorizationCredentials = Security(security),
                        db: Session = Depends(get_db)
                        ) -> dict:
    token = credentials.credentials
    email = await authtoken.refresh_token_email(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        print(f'\n\n{user.refresh_token}\n{token}\n\n')
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=MSC401_TOKEN)

    access_token = await authtoken.create_access_token(data={'sub': email})
    refresh_token = await authtoken.create_refresh_token(data={'sub': email})
    await repository_users.update_token(user, refresh_token, db)

    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': TOKEN_TYPE}


@router.post('/request_confirm_email', response_model=MessageRequest)
async def request_confirm_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)) -> dict:
    user = await repository_users.get_user_by_email(body.email, db)

    if user and user.confirmed:
        return {'message': EMAIL_ERROR_CONFIRMED}

    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)

    return {'message': EMAIL_INFO_CONFIRMED}


@router.get('/confirmed_email/{token}', response_model=MessageRequest)
async def confirmed_email(token: str, db: Session = Depends(get_db)) -> dict:
    email = await authtoken.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=MSC400_BAD_REQUEST)

    if user.confirmed:
        return {'message': EMAIL_ERROR_CONFIRMED}

    await repository_users.confirmed_email(user, db)

    return {'message': EMAIL_INFO_CONFIRM}


@router.post('/reset-password')
async def reset_password(
                         body: RequestEmail, 
                         background_tasks: BackgroundTasks, 
                         request: Request,
                         db: Session = Depends(get_db)
                         ) -> dict:

    user = await repository_users.get_user_by_email(body.email, db)
    
    if user:
        if user.confirmed:
            background_tasks.add_task(send_reset_password, user.email, user.username, request.base_url)

            return {'message': EMAIL_INFO_CONFIRMED}
        
        return {'message': EMAIL_INFO_CONFIRMED}
    
    return {'message': MSC401_EMAIL_UNKNOWN}


@router.post('/reset-password-request')
async def reset_password(
                         body: RequestEmail,
                         background_tasks: BackgroundTasks,
                         request: Request,
                         db: Session = Depends(get_db)
                         ) -> dict:

    user = await repository_users.get_user_by_email(body.email, db)

    if user:
        if user.confirmed:
            background_tasks.add_task(send_reset_password, user.email, user.username, request.base_url)

            return {'message': EMAIL_INFO_CONFIRMED}
        
        return {'message': EMAIL_INFO_CONFIRMED}
    
    return {'message': MSC401_EMAIL_UNKNOWN}


@router.get('/reset-password/done_request', response_class=HTMLResponse, description='Request password reset Page.')  
async def reset_password_done(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse('password_reset_done.html', {'request': request,
                                                                   'title': MSG_SENT_PASSWORD})


@router.post('/reset-password/confirm/{token}')
async def reset_password_confirm(
                                 background_tasks: BackgroundTasks, 
                                 request: Request,
                                 token: str,
                                 db: Session = Depends(get_db)
                                 ) -> dict:

    email: str = await authtoken.get_email_from_token(token)
    exist_user = await repository_users.get_user_by_email(email, db)
    if not exist_user:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=MSC503_UNKNOWN_USER)
    
    new_password: str = authpassword.get_new_password()
    password: str = authpassword.get_hash_password(new_password)
    
    updated_user: User = await repository_users.change_password_for_user(exist_user, password, db)
    if updated_user is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=MSC503_UNKNOWN_USER)

    background_tasks.add_task(send_new_password, updated_user.email, updated_user.username, request.base_url, new_password)  

    return {'user': updated_user, 'detail': MSG_PASSWORD_CHENGED}


@router.get('/reset-password/complete', response_class=HTMLResponse, description='Complete password reset Page.')
async def reset_password_complete(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse('password_reset_complete.html', {'request': request,
                                                                       'title': MSG_PASSWORD_RESET})
