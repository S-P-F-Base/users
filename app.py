import contextlib

from fastapi import FastAPI

from db_control import AccessDB, CredentialsDB, PermaLimitDB
from router.overlord_api import router as overlord_api_router


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    CredentialsDB.set_up()
    PermaLimitDB.set_up()
    #
    #
    AccessDB.set_up()

    try:
        yield

    finally:
        pass


app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.include_router(overlord_api_router)
