import logging
from functools import wraps
from typing import Sequence

from sqlalchemy import Column, Integer
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import DBAPIError
from sqlalchemy.future import Connection
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.expression import delete, insert, select, update

from app.exceptions import DBError
from settings import DB_PATH

Base = declarative_base()
engine = create_engine(DB_PATH, echo=True, pool_pre_ping=True)


class StudentGroup(Base):
    __tablename__ = "student_groups"

    id = Column(Integer, primary_key=True)
    course = Column(Integer, nullable=False)


def db_connect(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        buffer = None
        try:
            conn = engine.connect()
            buffer = func(*args, conn=conn, **kwargs)
        except DBAPIError as err:
            logging.error(f"Database error")
            raise DBError() from err
        except Exception as err:
            logging.critical(f"Unexpected error")
            raise DBError() from err
        finally:
            try:
                conn.close()
            except DBAPIError as err:
                logging.error(f"Database error")
                raise DBError() from err
        return buffer

    return wrapper


@db_connect
def ids_by_course(course: int, *, conn: Connection) -> Sequence[int]:
    ids = conn.execute(
        select(StudentGroup.id).where(StudentGroup.course == course)
    ).all()
    return [id_[0] for id_ in ids]


@db_connect
def delete_group(group_id: int, *, conn: Connection) -> None:
    conn.execute(delete(StudentGroup).where(StudentGroup.id == group_id))
    conn.commit()


@db_connect
def groups_ids(*, conn: Connection) -> Sequence[int]:
    ids = conn.execute(select(StudentGroup.id)).all()
    return [id_[0] for id_ in ids]


@db_connect
def add_group(group_id: int, course: int, *, conn: Connection) -> None:
    conn.execute(
        insert(StudentGroup),
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
        update(StudentGroup)
        .where(StudentGroup.id == group_id)
        .values(course=course)
    )
    conn.commit()
