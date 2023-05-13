from datetime import datetime, timedelta
import json
from typing import Optional

from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
import redis
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.db import get_db, get_redis
from src.repository import users as repository_users
from src.conf.messages import *


class AuthPassword:
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    def get_hash_password(self, password: str):
        return self.pwd_context.hash(password)

    def verify_password(self, password: str, hashed_password: str):
        return self.pwd_context.verify(password, hashed_password)


class AuthToken:
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl='/api/auth/login')

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(expires_delta)
            
        else:
            expire = datetime.utcnow() + timedelta(hours=1)

        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'access_token'})
        access_token = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)

        return access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(expires_delta)

        else:
            expire = datetime.utcnow() + timedelta(days=7)

        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'refresh_token'})
        refresh_token = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)

        return refresh_token

    async def create_email_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=1)
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
                                detail=MSC422_EMAIL_VERIFICATION)

    async def refresh_token_email(self, refresh_token: OAuth2PasswordBearer = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, self.ALGORITHM)
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                if email is None:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=MSC401_EMAIL)
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=MSC401_TOKEN_SCOPE)
            
        except:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=MSC401_CREDENTIALS)

        return email
    
    async def create_password_reset_token(self, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)

        else:
            expire = datetime.utcnow() + timedelta(minutes=25)

        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'password_reset_token'})
        encoded_password_reset_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

        return encoded_password_reset_token


class AuthUser(AuthToken):
    redis_client = get_redis()

    async def get_current_user(self, token: OAuth2PasswordBearer = Depends(AuthToken.oauth2_scheme), db: Session = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=MSC401_CREDENTIALS,
            headers={'WWW-Authenticate': TOKEN_TYPE},  # 'Bearer'
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
        
        user = self.redis_client.get(email) if self.redis_client else None

        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            user = {'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'refresh_token': user.refresh_token,
                    'roles': user.roles
                    }
            json_user = json.dumps(user)
            if user is None:
                raise credentials_exception
            
            self.redis_client.set(email, user) if self.redis_client else None
            self.redis_client.expire(email, 60) if self.redis_client else None

        else:
            user = json.loads(user)

        return user
