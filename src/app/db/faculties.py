from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import select

from app.db.common import Base, db_connect


class Faculty(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    student_groups = relationship("StudentGroup", back_populates="faculty")


@db_connect
async def add_faculty(name: str, *, session: AsyncSession) -> None:
    faculty = Faculty(name=name)
    session.add(faculty)
    await session.commit()


@db_connect
async def get_all_faculties(*, session: AsyncSession):
    faculties = await session.execute(select(Faculty))
    return faculties.all()
