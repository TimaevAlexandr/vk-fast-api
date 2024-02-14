from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from app.db.common import Base, db_connect


class Message(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    attachments = Column(JSON)
    author = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    groups = relationship("GroupMessage", back_populates="message")


@db_connect
async def add_message(
    text: str | None,
    attachments: list | None,
    author: int,
    *,
    session: AsyncSession,
) -> Message:
    message = Message(
        text=text,
        attachments=attachments,
        author=author,
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message
