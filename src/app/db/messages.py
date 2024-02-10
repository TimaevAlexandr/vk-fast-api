from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    PickleType,
    Text,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import select

from app.db.common import Base, db_connect


class Message(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    attachment = Column(PickleType)
    author = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    groups = relationship("GroupMessage", back_populates="message")


@db_connect
async def add_message(
    text: str | None,
    attachment: list | None,
    author: int,
    date: datetime | None = None,
    *,
    session: AsyncSession,
) -> int:
    message = Message(
        text=text,
        attachment=attachment,
        author=author,
        date=date,
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message.id


@db_connect
async def get_message(
    message_id: int,
    *,
    session: AsyncSession,
):
    return await session.scalar(
        select(Message).where(Message.id == message_id)
    )
