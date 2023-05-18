# from datetime import datetime
# import traceback

from fastapi import HTTPException, status
import redis
import redis.asyncio as aredis
from redis.exceptions import AuthenticationError
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from src.conf.config import settings
from src.conf.messages import MSC500_DATABASE_CONFIG, MSC500_DATABASE_CONNECT
from src.services.asyncdevlogging import async_logging_to_file


URI = settings.sqlalchemy_database_url


engine = create_engine(URI, echo=True)
DBSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = DBSession()
    try:
        yield db

    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

    finally:
        db.close()


def get_redis(is_async: bool = True):
    module = {
        True: aredis,
        False: redis
    }
    redis_module = module[is_async]
    try:
        if settings.redis_password and settings.redis_password != '0':
            redis_client = redis_module.Redis(
                                    host=settings.redis_host,
                                    port=settings.redis_port,
                                    db=0,
                                    password=settings.redis_password
                                    )

        else:
            redis_client = redis_module.Redis(
                                    host=settings.redis_host,
                                    port=settings.redis_port,
                                    db=0
                                    )

    except AuthenticationError as error:
        redis_client = None
        print(f'Authentication failed to connect to redis\n{error}')
        # await async_logging_to_file(f'\n500:\t{datetime.now()}\t{MSC500_DATABASE_CONFIG}: {err}\t{traceback.extract_stack(None, 2)[1][2]}')

    except Exception as error:
        redis_client = None
        print(f'Unable to connect to redis\n{error}')
        # await async_logging_to_file(f'\n500:\t{datetime.now()}\t{MSC500_DATABASE_CONNECT}: {err}\t{traceback.extract_stack(None, 2)[1][2]}')

    return redis_client if redis_client else None
