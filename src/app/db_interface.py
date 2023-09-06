import logging
from typing import Sequence

from consts import DB_PATH
from sqlalchemy import (
    Column,
    Connection,
    Integer,
    MetaData,
    Table,
    create_engine,
    delete,
    insert,
    inspect,
    select,
)
from sqlalchemy.exc import DBAPIError

engine = create_engine(DB_PATH, echo=True)
metadata = MetaData()

student_groups = Table(
    "student_groups",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("course", Integer, nullable=False),
)


def db_connect(func):
    def wrapper(*args, **kwargs):
        try:
            conn = engine.connect()
            func(*args, conn=conn, **kwargs)
            conn.close()
        except DBAPIError as error:
            logging.error(f"Database error {error}")
        except Exception as error:
            logging.critical(f"Unexpected error {error}")

    return wrapper


def init_database() -> None:
    if not inspect(engine).has_table("student_groups"):
        student_groups.create(engine)


@db_connect
def ids_by_course(course: int, *, conn: Connection) -> Sequence:
    ids = conn.execute(
        select(student_groups.c.id).where(student_groups.c.course == course)
    ).all()
    return [id_[0] for id_ in ids]


@db_connect
def delete_group(group_id: int, *, conn: Connection) -> None:
    conn.execute(delete(student_groups).where(student_groups.c.id == group_id))
    conn.commit()


@db_connect
def groups_ids(*, conn: Connection) -> Sequence:
    ids = conn.execute(select(student_groups.c.id)).all()
    return [id_[0] for id_ in ids]


@db_connect
def add_group(group_id: int, course: int, *, conn: Connection) -> None:
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
