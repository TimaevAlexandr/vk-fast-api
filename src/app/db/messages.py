from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import insert

from app.db.common import Base, db_connect


class Message(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    message = Column(Text)
    attachment = Column(String)
    date = Column(DateTime, nullable=False)
    author = Column(String, nullable=False)


@db_connect
async def add_message(
    message: str | None,
    attachment: str | None,
    date: datetime,
    author: str,
    *,
    session: AsyncSession
) -> None:
    await session.execute(
        insert(Message),  # type: ignore
        [
            {
                "message": message,
                "attachment": attachment,
                "date": date,
                "author": author,
            }
        ],
    )
    await session.commit()
