import logging
from functools import wraps
from typing import Sequence

from sqlalchemy import Column, Integer, MetaData, Table
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import DBAPIError
from sqlalchemy.future import Connection
from sqlalchemy.sql.expression import delete, insert, select, update

from settings import DB_PATH

engine = create_engine(DB_PATH, echo=True, pool_pre_ping=True)
metadata = MetaData()

student_groups = Table(
    "student_groups",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("course", Integer, nullable=False),
)


def db_connect(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        buffer = None
        try:
            conn = engine.connect()
            buffer = func(*args, conn=conn, **kwargs)
        except DBAPIError as error:
            logging.error(f"Database error {error}")
        except Exception as error:
            logging.critical(f"Unexpected error {error}")
        finally:
            try:
                conn.close()
            except DBAPIError as error:
                logging.error(f"Database error {error}")
        return buffer

    return wrapper


@db_connect
def ids_by_course(course: int, *, conn: Connection) -> Sequence[int]:
    ids = conn.execute(
        select(student_groups.c.id).where(student_groups.c.course == course)
    ).all()
    return [id_[0] for id_ in ids]


@db_connect
def delete_group(group_id: int, *, conn: Connection) -> None:
    conn.execute(delete(student_groups).where(student_groups.c.id == group_id))
    conn.commit()


@db_connect
def groups_ids(*, conn: Connection) -> Sequence[int]:
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


@db_connect
def change_group_course(
    group_id: int, course: int, *, conn: Connection
) -> None:
    conn.execute(
        update(student_groups)
        .where(student_groups.c.id == group_id)
        .values(course=course)
    )
    conn.commit()
