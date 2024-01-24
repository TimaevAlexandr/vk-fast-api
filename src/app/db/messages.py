from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import insert

from app.db.common import Base, db_connect


class Message(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    message = Column(Text)
    attachment = Column(String)
    date = Column(DateTime, nullable=False)
    admin_id = Column(Integer, ForeignKey("admin.id"), nullable=False)
    admin = relationship("Admin")


@db_connect
async def add_message(
    message: str | None,
    attachment: str | None,
    date: datetime,
    admin: int,
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
                "admin": admin,
            }
        ],
    )
    await session.commit()
