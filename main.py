from datetime import datetime
import traceback

from fastapi import Depends, FastAPI, HTTPException
from fastapi_limiter.depends import FastAPILimiter
from sqlalchemy import text
from sqlalchemy.orm import Session
import uvicorn

from src.conf import messages
from src.database.db import get_db, get_redis
from src.routes import auth, comments, images, users
from src.services.asyncdevlogging import async_logging_to_file


app = FastAPI()
app.include_router(auth.router, prefix='/api')
app.include_router(comments.router, prefix='/api')
app.include_router(images.router, prefix='/api')
app.include_router(users.router, prefix='/api')


@app.on_event('startup')
async def startup() -> None:
    await FastAPILimiter.init(get_redis())


@app.get('/api/healthchecker')
async def healthchecker(db: Session = Depends(get_db)) -> dict:
    try:
        # Make request
        result = db.execute(text('SELECT 1')).fetchone()
        if result is None:
            await async_logging_to_file(f'\n500:\t{datetime.now()}\t{messages.MSC500_DATABASE_CONNECT}\t{traceback.extract_stack(None, 2)[1][2]}')
            raise HTTPException(status_code=500, detail=messages.MSC500_DATABASE_CONFIG)

        return {'message': messages.WELCOME_FASTAPI}

    except Exception as e:
        await async_logging_to_file(f'\n500:\t{datetime.now()}\t{messages.MSC500_DATABASE_CONNECT}: {e}\t{traceback.extract_stack(None, 2)[1][2]}')
        raise HTTPException(status_code=500, detail=messages.MSC500_DATABASE_CONNECT)


@app.get('/')
def read_root() -> dict:
    return {'message': messages.WELCOME}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
