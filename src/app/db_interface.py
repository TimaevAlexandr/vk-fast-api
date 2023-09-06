from typing import Sequence

from consts import DB_PATH
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    Table,
    create_engine,
    delete,
    insert,
    inspect,
    select,
)

engine = create_engine(DB_PATH, echo=True)
metadata = MetaData()

student_groups = Table(
    "student_groups",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("course", Integer, nullable=False),
)


def init_database() -> None:
    if not inspect(engine).has_table("student_groups"):
        student_groups.create(engine)


def ids_by_course(course: int) -> Sequence:
    with engine.connect() as conn:
        ids = conn.execute(
            select(student_groups.c.id).where(
                student_groups.c.course == course
            )
        ).all()
        return [id_[0] for id_ in ids]


def delete_group(group_id: int) -> None:
    with engine.connect() as conn:
        conn.execute(
            delete(student_groups).where(student_groups.c.id == group_id)
        )
        conn.commit()


def groups_ids() -> Sequence:
    with engine.connect() as conn:
        ids = conn.execute(select(student_groups.c.id)).all()
        return [id_[0] for id_ in ids]


def add_group(group_id: int, course: int) -> None:
    with engine.connect() as conn:
        conn.execute(
            insert(student_groups),
            [
                {
                    "id": group_id,
                    "course": course,
                }
            ],
        )
        conn.commit()
