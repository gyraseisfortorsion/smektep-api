import time

from fastapi import FastAPI, Request
from fastapi.logger import logger as log
from fastapi.middleware.cors import CORSMiddleware
# from fastapi_jwt_auth import AuthJWT

from routes import router
from core import settings



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: change to configs.ALLOWED_HOSTS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# @AuthJWT.load_config
# def get_config():
#     return settings


# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     log.debug(f"Request: {request.method} {request.url} {request.client.host}")
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     response.headers["X-Process-Time"] = str(process_time)

#     return response