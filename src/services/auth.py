from datetime import datetime, timedelta
import traceback
import pickle
from typing import Optional

from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.conf.messages import *
from src.database.db import get_db, get_redis
from src.database.models import User
from src.repository import users as repository_users
from src.services.asyncdevlogging import async_logging_to_file
from src.services.generator_password import get_password


class AuthPassword:

    @staticmethod
    def get_hash_password(password: str) -> str:
        pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> str:
        pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

        return pwd_context.verify(password, hashed_password)
    
    @staticmethod
    def get_new_password(password_length: int = settings.password_length) -> str:
        return get_password(password_length)


class AuthToken:
    oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl='/api/auth/login')
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    credentials_exception = HTTPException(
                                          status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=MSC401_CREDENTIALS,
                                          headers={'WWW-Authenticate': TOKEN_TYPE},
                                          )

    @classmethod
    async def create_token(cls, data: dict, expires_delta: Optional[float] = None, token_type: str = None) -> str:
        to_encode = data.copy()
        token_type_mapping = {
                              'access_token': settings.access_token_timer,
                              'refresh_token': settings.refresh_token_timer,
                              'password_reset_token': settings.password_reset_token_timer,
                              'email_token': settings.email_token_timer,
                              }
        default_token_lifetime_limit = token_type_mapping.get(token_type, 0)

        if expires_delta:
            expire = datetime.utcnow() + timedelta(expires_delta)

        else:
            expire = datetime.utcnow() + timedelta(hours=default_token_lifetime_limit)

        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': token_type})
        token = jwt.encode(to_encode, AuthToken.SECRET_KEY, AuthToken.ALGORITHM)

        return token

    @classmethod
    async def get_email_from_token(cls, token: OAuth2PasswordBearer = Depends(oauth2_scheme), token_type: str = None) -> str:
        try:
            payload = jwt.decode(token, AuthToken.SECRET_KEY, algorithms=[AuthToken.ALGORITHM])
            email = payload['sub']
            if not token_type:
                return email
            
            elif payload['scope'] == token_type:
                if email is None:
                    raise AuthToken.credentials_exception  # MSC401_EMAIL ?
                
            else:
                raise AuthToken.credentials_exception  # MSC401_TOKEN_SCOPE ?

        except JWTError as e:
            await async_logging_to_file(f'\n3XX:\t{datetime.now()}\tJWTError: {e}\t{traceback.extract_stack(None, 2)[1][2]}')
            raise HTTPException(
                                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=MSC422_INVALID_TOKEN
                                )
        
        return email
    

    @staticmethod
    async def token_check(payload: dict, token_type: str = 'access_token') -> str:
        if payload['scope'] == token_type:
            email = payload['sub']
            if email is None:
                raise AuthToken.credentials_exception

        else:
            raise AuthToken.credentials_exception
        
        return email


class AuthUser(AuthToken):
    redis_client = get_redis(False)

    @classmethod
    async def clear_user_cash(cls, user_email) -> None:
        AuthUser.redis_client.delete(user_email)

    @classmethod
    async def get_current_user(cls, token: str = Depends(AuthToken.oauth2_scheme), db: Session = Depends(get_db)) -> dict:
        email = AuthToken.get_email_from_token(token, token_type='access_token')

        bl_token = AuthUser.redis_client.get(token)
        if bl_token:
            raise AuthUser.credentials_exception


        user: Optional[User] = AuthUser.redis_client.get(email) if AuthUser.redis_client else None
        if user is None:
            user: User = await repository_users.get_user_by_email(email, db)

            user = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'roles': user.roles,
                    'status_active': user.status_active,
                    }

            if user is None:
                raise AuthUser.credentials_exception

            AuthUser.redis_client.set(email, pickle.dumps(user)) if AuthUser.redis_client else None
            AuthUser.redis_client.expire(email, settings.redis_user_timer) if AuthUser.redis_client else None

        else:
            user: User = pickle.loads(user)

        if not user.get('status_active'):
            await async_logging_to_file(f'\n5XX:\t{datetime.now()}\tUser_status: {user["status_active"]}\t{traceback.extract_stack(None, 2)[1][2]}')
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=MSC403_USER_BANNED)

        return user


    @classmethod
    async def logout_user(cls, token: str = Depends(AuthToken.oauth2_scheme)) -> dict:
        try:
            payload = jwt.decode(token, AuthUser.SECRET_KEY, AuthUser.ALGORITHM)
            email = AuthUser.token_check(payload, token_type='access_token')

        except:
            raise AuthUser.credentials_exception

        now = datetime.timestamp(datetime.now())
        time_delta = payload['exp'] - now + settings.redis_addition_lag
        AuthUser.redis_client.set(token, 'True')
        AuthUser.redis_client.expire(token, int(time_delta))


security = HTTPBearer()
