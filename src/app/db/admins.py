from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import insert, select

from app.db.common import Base, db_connect


class Admin(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    is_superuser = Column(Boolean, nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.id"), nullable=True)


@db_connect
async def add_admin(
    admin_id: int,
    is_superuser: bool,
    faculty_id: int,
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
            }
        ],
    )
    await session.commit()


@db_connect
async def get_all_admins(*, session: AsyncSession):
    admins = await session.execute(select(Admin))
    return admins.all()


@db_connect
async def get_all_superusers(*, session: AsyncSession):
    superusers = await session.execute(select(Admin).where(Admin.is_superuser))
    return superusers.all()
