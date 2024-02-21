from typing import Iterable

from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import update, insert, select

from app.db.common import Base, db_connect


class Admin(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    is_superuser = Column(Boolean, nullable=False)
    is_archived = Column(Boolean, nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.id"), nullable=True)


@db_connect
async def add_admin(
    admin_id: int,
    is_superuser: bool,
    faculty_id: int,
    is_archived: bool,
    *,
    session: AsyncSession
) -> None:
    await session.execute(
        insert(Admin),  # type: ignore
        [
            {
                "id": admin_id,
                "is_superuser": is_superuser,
                "faculty_id": faculty_id,
                "is_archived": is_archived,
            }
        ],
    )
    await session.commit()


@db_connect
async def get_all_admins(*, session: AsyncSession) -> Iterable[Admin] | None:
    statement = select(Admin)
    result = await session.execute(statement)
    admins = result.scalars().all()
    return admins  # type: ignore


@db_connect
async def get_all_superusers(
    *, session: AsyncSession
) -> Iterable[Admin] | None:
    superusers = await session.execute(select(Admin).where(Admin.is_superuser))
    return superusers.all()  # type: ignore


@db_connect
async def archive_admin(admin_id: int, *, session: AsyncSession) -> None:
    statement = update(Admin).where(Admin.id == admin_id).values(is_archived=True)
    await session.execute(statement)
    await session.commit()


@db_connect
async def get_admin_by_id(
    admin_id: int, *, session: AsyncSession
) -> Admin | None:
    result = await session.execute(
        select(Admin).where(Admin.id == int(admin_id))
    )
    admin = result.scalar_one_or_none()
    return admin  # type: ignore


@db_connect
async def restore_admin(
    admin_id: int, *, session: AsyncSession
) -> None:
    statement = update(Admin).where(Admin.id == admin_id).values(is_archived=False)
    await session.execute(statement)
    await session.commit()