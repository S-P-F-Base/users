from fastapi import APIRouter
from fastapi.responses import JSONResponse

from config import AccessKeys

router = APIRouter()


@router.get("/users/access_info")
async def access_get_all_keys():
    return JSONResponse(
        {
            "all_access_keys": AccessKeys.get_all_access_keys(),
            "base_access": AccessKeys.get_base_access(),
        },
        status_code=200,
    )
    