from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from config import USER_GET_TYPE_L
from db_control import CredentialsDB

router = APIRouter()


@router.get("/users/{value}")
async def get_users_cred(value: str, type: USER_GET_TYPE_L | None = None):
    _disp = {
        "id": CredentialsDB.get_by_id,
        "discord": CredentialsDB.get_by_discord,
        "steam64": CredentialsDB.get_by_steam,
    }

    resolve_type = type or "id"
    func = _disp.get(resolve_type)

    if func is None:
        raise HTTPException(status_code=400, detail=f"invalid resolve type: {type}")

    if resolve_type == "id":
        try:
            value_casted = int(value)

        except ValueError:
            raise HTTPException(400, detail="id must be integer")

    else:
        value_casted = value

    resp = func(value_casted)
    return JSONResponse(resp, status_code=200)
