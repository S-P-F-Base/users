from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/ping")
async def ping_overlord():
    return JSONResponse({"ok": True}, status_code=200)
