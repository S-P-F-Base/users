from fastapi import APIRouter
from fastapi.responses import JSONResponse

from config import AccessKeys

router = APIRouter()


@router.get("/users/info/access")
async def info_access():
    return JSONResponse(
        {
            "all_access_keys": AccessKeys.get_all_access_keys(),
            "base_access": AccessKeys.get_base_access(),
        },
        status_code=200,
    )


@router.get("/users/info/user_get_type")
async def info_user_get_type():
    return JSONResponse(
        ["id", "discord", "steam64"],
        status_code=200,
    )
