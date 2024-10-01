from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from foundation.core.config import settings

"""
This module sets up the configuration for the asynchronous SQLAlchemy engine and session factory.

Objects:
    engine: An asynchronous database engine configured with the DATABASE_URL, with SQL query logging enabled.
    async_sessionmaker: A session factory that creates new instances of AsyncSession using the engine.

Usage:
    The async_sessionmaker can be imported and used to create new AsyncSession instances for database operations.

Example:
    ```python
    from your_module.database import async_sessionmaker
    
    async def get_users():
        async with async_sessionmaker() as session:
            result = await session.execute("SELECT * FROM users")
            users = result.fetchall()
            return users
    ```
"""

# an AsyncEngine, which the AsyncSession will use for connection resources
# see site-packages/sqlalchemy/ext/asyncio/session.py:1622
engine = create_async_engine(settings.postgres_dsn, echo=True)

# create a reusable factory for new AsyncSession instances
async_sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
