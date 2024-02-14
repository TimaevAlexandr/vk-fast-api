from typing import Iterable

from sqlalchemy import Boolean, Column, ForeignKey, Integer, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import delete, insert, select, update

from app.db.common import Base, db_connect
from app.db.messages import Message


class StudentGroup(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "student_groups"

    id = Column(Integer, primary_key=True)
    course = Column(Integer, nullable=False)
    messages = relationship("GroupMessage", back_populates="group")


class GroupMessage(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "group_message"

    student_group_id = Column(
        ForeignKey("student_groups.id"), primary_key=True
    )
    message_id = Column(ForeignKey("messages.id"), primary_key=True)
    received = Column(Boolean, nullable=False)
    message = relationship("Message", back_populates="groups")
    group = relationship("StudentGroup", back_populates="messages")


@db_connect
async def connect_message_to_group(
    group_id: int,
    message_id: int,
    received: bool,
    *,
    session: AsyncSession,
) -> GroupMessage:
    group_message = GroupMessage(
        student_group_id=group_id, message_id=message_id, received=received
    )
    session.add(group_message)
    await session.commit()
    await session.refresh(group_message)
    return group_message


@db_connect
async def count_messages_by_group(
    group_id: int,
    received: bool,
    *,
    session: AsyncSession,
) -> int:
    return int(
        await session.scalar(
            select(func.count(GroupMessage.student_group_id)).where(
                (GroupMessage.student_group_id == group_id)
                & (GroupMessage.received == received)
            )
        )
    )


@db_connect
async def count_messages_by_courses(
    *,
    session: AsyncSession,
) -> list[tuple[int, int]]:
    return list(
        (
            await session.execute(
                select(
                    StudentGroup.course,
                    func.count(Message.id).label("count_messages"),
                )
                .outerjoin(
                    GroupMessage,
                    StudentGroup.id == GroupMessage.student_group_id,
                )
                .outerjoin(Message, GroupMessage.message_id == Message.id)
                .group_by(StudentGroup.course)
                .order_by(StudentGroup.course)
            )
        ).all()
    )


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
async def get_groups_ids(*, session: AsyncSession) -> Iterable[int]:
    group_ids = (await session.execute(select(StudentGroup))).all()
    return [group_id[0].id for group_id in group_ids]


@db_connect
async def add_group(
    group_id: int, course: int, *, session: AsyncSession
) -> None:
    await session.execute(
        insert(StudentGroup),  # type: ignore
        [
            {
                "id": group_id,
                "course": course,
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
