from datetime import datetime
import traceback

from fastapi import Depends, FastAPI, HTTPException
from fastapi_limiter.depends import FastAPILimiter
from sqlalchemy import text
from sqlalchemy.orm import Session
import uvicorn

from src.conf import messages
from src.database.db import get_db, get_redis
from src.routes import auth, comments, images, users, ratings
from src.services.asyncdevlogging import async_logging_to_file


app = FastAPI()
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(images.router, prefix='/api')
app.include_router(comments.router, prefix='/api')
app.include_router(ratings.router, prefix='/api')


@app.on_event('startup')
async def startup() -> None:
    await FastAPILimiter.init(get_redis())


@app.get('/api/healthchecker')
async def healthchecker(db: Session = Depends(get_db)) -> dict:
    """
    The healthchecker function is a simple function that returns a JSON object with the message 'Welcome to FastAPI!'
    This function is used by the healthchecker endpoint, which can be accessed at http://localhost:8000/healthchecker.
    The purpose of this endpoint is to provide an easy way for users and developers to check if the API server has been
    successfully deployed and configured. This endpoint should return a 200 status code when everything works as
    expected.

    :param db: Session: Get the database session
    :return: A dict with the message
    :doc-author: Trelent
    """
    try:
        # Make request
        result = db.execute(text('SELECT 1')).fetchone()
        if result is None:
            function_name = traceback.extract_stack(None, 2)[1][2]
            add_log = f'\n500:\t{datetime.now()}\t{messages.MSC500_DATABASE_CONNECT}\t{function_name}'
            await async_logging_to_file(add_log)
            raise HTTPException(status_code=500, detail=messages.MSC500_DATABASE_CONFIG)

        function_name = traceback.extract_stack(None, 2)[1][2]
        add_log = f'\n000:\t{datetime.now()}\t{messages.WELCOME_FASTAPI}\t{function_name}'
        await async_logging_to_file(add_log)

        return {'message': messages.WELCOME_FASTAPI}

    except Exception as e:
        function_name = traceback.extract_stack(None, 2)[1][2]
        add_log = f'\n000:\t{datetime.now()}\t{messages.MSC500_DATABASE_CONNECT}: {e}\t{function_name}'
        await async_logging_to_file(add_log)
        raise HTTPException(status_code=500, detail=messages.MSC500_DATABASE_CONNECT)


@app.get('/')
def read_root() -> dict:
    """
    The read_root function returns a dictionary with the key 'message' and value of `WELCOME`

    :return: A dictionary with the key 'message' and the value of `welcome`
    :doc-author: Trelent
    """
    return {'message': messages.WELCOME}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
