from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    PickleType,
    Text,
    ForeignKey
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship

from app.db.common import Base, db_connect


class Message(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    attachment = Column(PickleType)
    date = Column(DateTime, nullable=False)
    author = Column(Integer, ForeignKey("admin.id"), nullable=False)
    admin = relationship("Admin")


@db_connect
async def add_message(
    text: str | None,
    attachment: list | None,
    date: datetime,
    author: str,
    *,
    session: AsyncSession,
) -> Message:
    message = Message(
        text=text, attachment=attachment, date=date, author=author
    )
    session.add(message)
    await session.commit()
    return message
