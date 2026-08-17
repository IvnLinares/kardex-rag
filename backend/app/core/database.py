from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import settings

engine: AsyncEngine = create_async_engine(settings.database_url_asyncpg, pool_pre_ping=True)
