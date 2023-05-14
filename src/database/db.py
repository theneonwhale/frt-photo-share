import configparser
import pathlib

from fastapi import HTTPException, status
import redis
import redis.asyncio as aredis
from redis.exceptions import AuthenticationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from src.conf.config import settings


URI = settings.sqlalchemy_database_url


engine = create_engine(URI, echo=True)
DBSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# Dependency
def get_db():
    db = DBSession()
    try:
        yield db

    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    
    finally:
        db.close()


def get_async_redis():
    try:
        if settings.redis_password and settings.redis_password != '0':
            redis_client = aredis.Redis(
                                    host=settings.redis_host, 
                                    port=settings.redis_port, 
                                    db=0, 
                                    password=settings.redis_password
                                    )
            
        else:
            redis_client = aredis.Redis(
                                    host=settings.redis_host, 
                                    port=settings.redis_port, 
                                    db=0
                                    )
            
    except AuthenticationError as error:
        redis_client = None
        print(f'Authentication failed to connect to redis\n{error}')
        
    except Exception as error:
        redis_client = None
        print(f'Unable to connect to redis\n{error}')

    return redis_client if redis_client else None


def get_redis():
    try:
        if settings.redis_password and settings.redis_password != '0':
            redis_client = redis.Redis(
                                    host=settings.redis_host, 
                                    port=settings.redis_port, 
                                    db=0, 
                                    password=settings.redis_password
                                    )
            
        else:
            redis_client = redis.Redis(
                                    host=settings.redis_host, 
                                    port=settings.redis_port, 
                                    db=0
                                    )
            
    except AuthenticationError as error:
        redis_client = None
        print(f'Authentication failed to connect to redis\n{error}')
        
    except Exception as error:
        redis_client = None
        print(f'Unable to connect to redis\n{error}')

    return redis_client if redis_client else None
