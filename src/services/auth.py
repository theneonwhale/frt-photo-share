from datetime import datetime, timedelta
import traceback
import pickle
from typing import Optional
import secrets
import string

from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.conf import messages
from src.database.db import get_db, get_redis
from src.database.models import User
from src.repository import users as repository_users
from src.services.asyncdevlogging import async_logging_to_file


class AuthPassword:
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    def get_hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> str:
        return self.pwd_context.verify(password, hashed_password)

    def get_new_password(self, password_length: int = settings.password_length, meeting_limit: int = 2) -> str:
        letters = string.ascii_letters
        digits = string.digits
        special_chars = string.punctuation

        alphabet = letters + digits + special_chars

        while True:
            pwd = ''
            for i in range(password_length):
                pwd += ''.join(secrets.choice(alphabet))

            if (any(char in special_chars for char in pwd) and
                    sum(char in digits for char in pwd) >= meeting_limit):
                break

        return self.pwd_context.hash(pwd)


class AuthToken:
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl='/api/auth/login')

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(expires_delta)

        else:
            expire = datetime.utcnow() + timedelta(hours=settings.access_token_timer)

        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'access_token'})
        access_token = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)

        return access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(expires_delta)

        else:
            expire = datetime.utcnow() + timedelta(days=settings.refresh_token_timer)

        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'refresh_token'})
        refresh_token = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)

        return refresh_token

    async def create_email_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=settings.email_token_timer)
        to_encode.update({'iat': datetime.utcnow(), 'exp': expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)

        return token

    async def get_email_from_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload['sub']

            return email

        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=messages.MSC422_EMAIL_VERIFICATION)

    async def refresh_token_email(self, refresh_token: OAuth2PasswordBearer = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, self.ALGORITHM)
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                if email is None:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.MSC401_EMAIL)
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.MSC401_TOKEN_SCOPE)

        except:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.MSC401_CREDENTIALS)

        return email

    async def create_password_reset_token(self, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)

        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.password_reset_token_timer)

        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'password_reset_token'})
        encoded_password_reset_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

        return encoded_password_reset_token


class AuthUser(AuthToken):
    redis_client = get_redis(False)

    async def clear_user_cash(self, user_email):
        self.redis_client.delete(user_email)

    async def get_current_user(self, token: str = Depends(AuthToken.oauth2_scheme),
                               db: Session = Depends(get_db)) -> dict:
        credentials_exception = HTTPException(

                                              status_code=status.HTTP_401_UNAUTHORIZED,
                                              detail=messages.MSC401_CREDENTIALS,
                                              headers={'WWW-Authenticate': messages.TOKEN_TYPE},
                                              )
        try:
            payload = jwt.decode(token, self.SECRET_KEY, self.ALGORITHM)
            if payload['scope'] == 'access_token':
                email = payload['sub']
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception

        except JWTError as e:
            await async_logging_to_file(
                f'\n3XX:\t{datetime.now()}\tJWTError: {e}\t{traceback.extract_stack(None, 2)[1][2]}')

            raise credentials_exception

        bl_token = self.redis_client.get(token)
        if bl_token:
            raise credentials_exception

        user: Optional[User] = self.redis_client.get(email) if self.redis_client else None
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
                raise credentials_exception

            self.redis_client.set(email, pickle.dumps(user)) if self.redis_client else None
            self.redis_client.expire(email, settings.redis_user_timer) if self.redis_client else None

        else:
            user: User = pickle.loads(user)

        if not user.get('status_active'):

            await async_logging_to_file(f'\n5XX:\t{datetime.now()}\tUser_status: {user["status_active"]}\t{traceback.extract_stack(None, 2)[1][2]}')
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.MSC403_USER_BANNED)

        return user

    async def logout_user(self, token: str = Depends(AuthToken.oauth2_scheme)) -> dict:
        credentials_exception = HTTPException(

                                              status_code=status.HTTP_401_UNAUTHORIZED,
                                              detail=messages.MSC401_CREDENTIALS,
                                              headers={'WWW-Authenticate': messages.TOKEN_TYPE},
                                              )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, self.ALGORITHM)
            if payload['scope'] == 'access_token':
                email = payload['sub']
                if email is None:
                    raise credentials_exception

            else:
                raise credentials_exception

        except:
            raise credentials_exception

        now = datetime.timestamp(datetime.now())
        time_delta = payload['exp'] - now + settings.redis_addition_lag
        self.redis_client.set(token, 'True')
        self.redis_client.expire(token, int(time_delta))


authpassword = AuthPassword()
authtoken = AuthToken()
authuser = AuthUser()
security = HTTPBearer()
