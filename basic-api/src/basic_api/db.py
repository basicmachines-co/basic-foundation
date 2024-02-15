from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from basic_api.config import settings

DATABASE_URL = settings.postgres_dsn

# an AsyncEngine, which the AsyncSession will use for connection resources
# see site-packages/sqlalchemy/ext/asyncio/session.py:1622
engine = create_async_engine(DATABASE_URL, echo=True)

# create a reusable factory for new AsyncSession instances
async_session = async_sessionmaker(engine, expire_on_commit=False)
