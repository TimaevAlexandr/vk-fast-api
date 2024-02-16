from datetime import datetime
from typing import Iterable

from sqlalchemy import Boolean, Column, ForeignKey, Integer, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.sql.expression import delete, insert, select, update

from app.db.common import Base, db_connect
from app.db.messages import add_message


class StudentGroup(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "student_groups"

    id = Column(Integer, primary_key=True)
    course = Column(Integer, nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.id"), nullable=True)
    faculty = relationship("Faculty")
    messages = relationship("GroupMessage")


class GroupMessage(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "group_message"

    student_groups_id = Column(
        ForeignKey("student_groups.id"), primary_key=True
    )
    messages_id = Column(ForeignKey("messages.id"), primary_key=True)
    received = Column(Boolean, nullable=False)
    message = relationship("Message")


@db_connect
async def connect_message_to_group(
    group_id: int,
    text: str | None,
    attachment: list | None,
    date: datetime,
    author: int,
    received: bool,
    *,
    session: AsyncSession,
) -> None:
    group = await session.scalar(
        select(StudentGroup)
        .where(StudentGroup.id == group_id)
        .options(
            selectinload(StudentGroup.messages),
        ),
    )
    association = GroupMessage(received=received)
    association.message = await add_message(text, attachment, date, author)
    group.messages.append(association)

    await session.commit()


@db_connect
async def delete_group(group_id: int, *, session: AsyncSession) -> None:
    await session.execute(
        delete(StudentGroup).where(StudentGroup.id == group_id)  # type: ignore
    )
    await session.commit()


@db_connect
async def get_group_ids_by_course(
    course: int, *, session: AsyncSession
) -> Iterable[int]:
    group_ids = await session.execute(
        select(StudentGroup).where(StudentGroup.course == course)
    )
    return [group_id[0].id for group_id in group_ids]


@db_connect
async def get_course_by_group_id(
    group_id: int, *, session: AsyncSession
) -> int | None:
    course: int | None = await session.scalar(
        select(StudentGroup.course).where(StudentGroup.id == group_id)
    )
    return course


@db_connect
async def get_group_ids_by_faculty_id(
    faculty_id: int, *, session: AsyncSession
) -> Iterable[int]:
    group_ids = await session.execute(
        select(StudentGroup).where(StudentGroup.faculty_id == faculty_id)
    )
    return [group_id[0].id for group_id in group_ids]


@db_connect
async def get_groups_ids(*, session: AsyncSession) -> Iterable[int]:
    groups = (await session.execute(select(StudentGroup))).all()
    return [group[0].id for group in groups if group[0].course != -1]


@db_connect
async def add_group(
    group_id: int, course: int, faculty_id: int, *, session: AsyncSession
) -> None:
    await session.execute(
        insert(StudentGroup),  # type: ignore
        [
            {
                "id": group_id,
                "course": course,
                "faculty_id": faculty_id,
            }
        ],
    )
    await session.commit()


@db_connect
async def change_group_course(
    group_id: int, course: int, *, session: AsyncSession
) -> None:
    await session.execute(
        update(StudentGroup)  # type: ignore
        .where(StudentGroup.id == group_id)
        .values(course=course)
    )
    await session.commit()


@db_connect
async def get_group_ids_by_course_faculty_id(
    course: int, faculty_id: int, *, session: AsyncSession
) -> list[int]:
    group_ids = await session.execute(
        select(StudentGroup.id).where(
            and_(
                StudentGroup.course == course,
                StudentGroup.faculty_id == faculty_id,
            )
        )
    )
    return [group_id[0] for group_id in group_ids]
