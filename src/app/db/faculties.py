from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import insert, select

from app.db.common import Base, db_connect


class Faculty(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True)
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
