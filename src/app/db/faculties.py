from sqlalchemy import Column, Integer, Sequence, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import insert, select

from app.db.common import Base, db_connect


class Faculty(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "faculty"

    id = Column(
        Integer, Sequence("faculty_id_seq"), primary_key=True, nullable=False
    )
    name = Column(Text, nullable=False)


@db_connect
async def add_faculty(
    faculty_id: int, name: str, *, session: AsyncSession
) -> None:
    await session.execute(
        insert(Faculty),  # type: ignore
        [
            {
                "id": faculty_id,
                "name": name,
            }
        ],
    )
    await session.commit()


@db_connect
async def get_all_faculties(*, session: AsyncSession):
    faculties = await session.execute(select(Faculty))
    return faculties.all()


@db_connect
async def get_faculty_id(name: str, *, session: AsyncSession):
    result = await session.execute(select(Faculty).where(Faculty.name == name))
    faculty = result.scalar_one_or_none()
    if faculty:
        return faculty.id
    return None


@db_connect
async def get_faculty_name(id: int, *, session: AsyncSession):
    result = await session.execute(select(Faculty).where(Faculty.id == id))
    faculty = result.scalar_one_or_none()
    if faculty:
        return faculty.name
    return None
