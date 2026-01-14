import contextlib

from fastapi import FastAPI

from db_control import AccessDB, CredentialsDB, DbCharDB, PermaLimitDB, TimedLimitDB
from router.info_api import router as info_api_router
from router.overlord_api import router as overlord_api_router


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    CredentialsDB.set_up()
    PermaLimitDB.set_up()
    TimedLimitDB.set_up()
    DbCharDB.set_up()
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

app.include_router(info_api_router)
app.include_router(overlord_api_router)
