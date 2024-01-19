import logging
from functools import wraps

from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.exceptions import DBError
from settings import DB_PATH

Base = declarative_base()
engine = create_async_engine(DB_PATH, echo=True, pool_pre_ping=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


def db_connect(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with SessionLocal() as session:
            try:
                return await func(*args, session=session, **kwargs)
            except DBAPIError as err:
                logging.error("Database error")
                raise DBError() from err
            except Exception as err:
                logging.critical("Unexpected error")
                raise DBError() from err

    return wrapper
