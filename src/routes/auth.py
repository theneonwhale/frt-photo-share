from fastapi import (
                     APIRouter,
                     BackgroundTasks,
                     Depends,
                     HTTPException,
                     Request,
                     status,
                     Security,
                     )
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from starlette.templating import _TemplateResponse
from sqlalchemy.orm import Session

from src.conf import messages
from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.schemas.users import MessageResponse, RequestEmail, Token, UserModel, UserResponse
from src.services.auth import AuthPassword, AuthToken, AuthUser, security
from src.services.email import send_email, send_new_password, send_reset_password


router = APIRouter(prefix='/auth', tags=['auth'])
templates = Jinja2Templates(directory='src/services/templates')


@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             description='Create new user')
async def sign_up(
                  body: UserModel,
                  background_tasks: BackgroundTasks,
                  request: Request,
                  db: Session = Depends(get_db)
                  ) -> User:
    """
    The sign_up function creates a new user in the database.

    :param body: UserModel: Get the data from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background queue
    :param request: Request: Get the base_url of the application
    :param db: Session: Get the database session and pass it to the repository layer
    :return: The new user created
    :doc-author: Trelent
    """
    check_user = await repository_users.get_user_by_email(body.email, db)
    if check_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.MSC409_CONFLICT)

    body.password = AuthPassword.get_hash_password(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))

    return new_user


@router.post('/login', response_model=Token)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict:
    """
    The login function is used to authenticate a user.
        It takes the username and password from the request body,
        checks if they are correct, and returns an access token.

    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: Session: Get a database session
    :return: A new access token and a refresh token
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.MSC401_EMAIL)

    if not AuthPassword.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.MSC401_PASSWORD)

    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.MSC401_EMAIL_UNKNOWN)

    access_token = await AuthToken.create_token(data={'sub': user.email}, token_type='access_token')
    refresh_token = await AuthToken.create_token(data={'sub': user.email}, token_type='refresh_token')
    await repository_users.update_token(user, refresh_token, db)

    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': messages.TOKEN_TYPE}


@router.get("/logout", response_class=HTMLResponse)
async def logout(
           credentials: HTTPAuthorizationCredentials = Security(security),
           current_user: dict = Depends(AuthUser.logout_user)
           ) -> RedirectResponse:
    """
    The logout function is used to logout a user from the system.

    :param credentials: HTTPAuthorizationCredentials: Get the credentials of the user
    :param current_user: dict: Get the current user from the database
    :return: A redirectresponse object with a status code of 205
    :doc-author: Trelent
    """
    resp = RedirectResponse(url="/login", status_code=status.HTTP_205_RESET_CONTENT)

    return resp


@router.get('/refresh_token', response_model=Token)
async def refresh_token(
                        credentials: HTTPAuthorizationCredentials = Security(security),
                        db: Session = Depends(get_db)
                        ) -> dict:
    """
    The refresh_token function is used to refresh the access_token.
        The function takes in a token and an email, then checks if the user exists.
        If so, it creates new tokens for that user and returns them.

    :param credentials: HTTPAuthorizationCredentials: Get the token from the request header
    :param db: Session: Access the database
    :return: A new access_token and refresh_token
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = await AuthToken.get_email_from_token(token, 'refresh_token')
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.MSC401_TOKEN)

    access_token = await AuthToken.create_token(data={'sub': user.email}, token_type='access_token')
    refresh_token = await AuthToken.create_token(data={'sub': user.email}, token_type='refresh_token')
    await repository_users.update_token(user, refresh_token, db)

    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': messages.TOKEN_TYPE}


@router.post('/request_confirm_email', response_model=MessageResponse)
async def request_confirm_email(
                                body: RequestEmail,
                                background_tasks: BackgroundTasks,
                                request: Request,
                                db: Session = Depends(get_db)
                                ) -> dict:
    """
    The request_confirm_email function is used to send a confirmation email to the user.
        The function takes in an email address and sends a confirmation link to that address.
        If the user already has an account, they will be sent another confirmation link.

    :param body: RequestEmail: Get the email address from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background
    :param request: Request: Get the base_url of the application
    :param db: Session: Get a database session from the dependency injection container
    :return: A dictionary with a message
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user and user.confirmed:
        return {'message': messages.EMAIL_ERROR_CONFIRMED}

    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)

    return {'message': messages.EMAIL_INFO_CONFIRMED}


@router.get('/confirmed_email/{token}', response_model=MessageResponse)
async def confirmed_email(token: str, db: Session = Depends(get_db)) -> dict:
    """
    The confirmed_email function is used to confirm the email of a user.
        It takes in a token and returns an object with the message 'Email confirmed' if successful.

    :param token: str: Get the email from the token
    :param db: Session: Get a database session
    :return: A dictionary with a message
    :doc-author: Trelent
    """
    email = await AuthToken.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.MSC400_BAD_REQUEST)

    if user.confirmed:
        return {'message': messages.EMAIL_ERROR_CONFIRMED}

    await repository_users.confirmed_email(user, db)

    return {'message': messages.EMAIL_INFO_CONFIRM}


@router.post('/reset-password')
async def reset_password(
                         body: RequestEmail,
                         background_tasks: BackgroundTasks,
                         request: Request,
                         db: Session = Depends(get_db)
                         ) -> dict:
    """
    The reset_password function is used to send a password reset email to the user.
        The function takes in an email address and sends a password reset link to that
        address if it exists in the database. If not, then an error message is returned.

    :param body: RequestEmail: Receive the email from the user
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the application
    :param db: Session: Get the database session
    :return: A message to the user
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user:
        if user.confirmed:
            background_tasks.add_task(send_reset_password, user.email, user.username, request.base_url)

            return {'message': messages.MSG_SENT_PASSWORD}

        return {'message': messages.EMAIL_INFO_CONFIRMED}

    return {'message': messages.MSC401_EMAIL_UNKNOWN}


@router.get('/reset-password/done_request', response_class=HTMLResponse, description='Request password reset Page.')
async def reset_password_done(request: Request) -> _TemplateResponse:
    """
    The reset_password_done function is called when the user clicks on the link in their email.
    It displays a message that says `Your password has been reset.`

    :param request: Request: Get the request object
    :return: A templateresponse object
    :doc-author: Trelent
    """
    return templates.TemplateResponse('password_reset_done.html', {'request': request,
                                                                   'title': messages.MSG_SENT_PASSWORD})


@router.post('/reset-password/confirm/{token}')
async def reset_password_confirm(
                                 background_tasks: BackgroundTasks,
                                 request: Request,
                                 token: str,
                                 db: Session = Depends(get_db)
                                 ) -> dict:
    """
    The reset_password_confirm function is used to reset a user's password.
        It takes the following parameters:
            background_tasks: BackgroundTasks,
            request: Request,
            token: str,
            db: Session = Depends(get_db)

    :param background_tasks: BackgroundTasks: Add a background task to the queue
    :param request: Request: Get the base_url of the application
    :param token: str: Get the email from the token
    :param db: Session: Get the database session
    :return: A dict with the user and a message
    :doc-author: Trelent
    """
    email: str = await AuthToken.get_email_from_token(token)
    exist_user = await repository_users.get_user_by_email(email, db)
    if not exist_user:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=messages.MSC503_UNKNOWN_USER)

    new_password: str = AuthPassword.get_new_password()
    password: str = AuthPassword.get_hash_password(new_password)

    updated_user: User = await repository_users.change_password_for_user(exist_user, password, db)
    if updated_user is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=messages.MSC503_UNKNOWN_USER)

    background_tasks.add_task(
                              send_new_password,
                              updated_user.email,
                              updated_user.username,
                              request.base_url,
                              new_password
                              )

    return {'user': updated_user, 'detail': messages.MSG_PASSWORD_CHENGED}


@router.get('/reset-password/complete', response_class=HTMLResponse, description='Complete password reset Page.')
async def reset_password_complete(request: Request) -> _TemplateResponse:
    """
    The reset_password_complete function is called when the user has successfully reset their password.
    It renders a template that informs the user of this fact.

    :param request: Request: Get the request object
    :return: The password_reset_complete
    :doc-author: Trelent
    """
    return templates.TemplateResponse('password_reset_complete.html', {'request': request,
                                                                       'title': messages.MSG_PASSWORD_RESET})
