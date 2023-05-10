from fastapi import FastAPI
import uvicorn

from src.conf.messages import WELCOME
# from src.routes import pictures


app = FastAPI()
# app.include_router(pictures.router, prefix='/api')


@app.get('/')
def read_root():
    return {'message': WELCOME}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    