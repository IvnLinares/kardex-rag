from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import engine

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
