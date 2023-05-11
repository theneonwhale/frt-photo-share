from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
import uvicorn

from src.conf.messages import WELCOME
from src.database.db import get_db
# from src.routes import pictures


app = FastAPI()
# app.include_router(pictures.router, prefix='/api')


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")

        
 @app.get('/')
def read_root():
    return {'message': WELCOME}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
