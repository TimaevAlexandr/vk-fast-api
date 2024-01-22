from sqlalchemy import Boolean, Column, ForeignKey, Integer, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import select

from app.db.common import Base, db_connect


class Faculty(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    student_groups = relationship("StudentGroup", back_populates="faculty")


class Admin(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True)
    is_superuser = Column(Boolean, nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.id"), nullable=False)
    faculty = relationship("Faculty", back_populates="admins")


@db_connect
async def add_faculty(name: str, *, session: AsyncSession) -> None:
    faculty = Faculty(name=name)
    session.add(faculty)
    await session.commit()


@db_connect
async def add_admin(
    is_superuser: bool, faculty_id: int, *, session: AsyncSession
) -> None:
    admin = Admin(is_superuser=is_superuser, faculty_id=faculty_id)
    session.add(admin)
    await session.commit()


@db_connect
async def get_all_admins(*, session: AsyncSession):
    admins = await session.execute(select(Admin))
    return admins.all()


@db_connect
async def get_all_faculties(*, session: AsyncSession):
    faculties = await session.execute(select(Faculty))
    return faculties.all()


@db_connect
async def get_all_superusers(*, session: AsyncSession):
    superusers = await session.execute(
        select(Admin).where(Admin.is_superuser is True)
    )
    return superusers.all()
