import pytest
from sqlalchemy import select

from app.db.common import engine
from app.db.faculties import (
    Faculty,
    add_faculty,
    get_all_faculties,
    get_faculty_id,
)


@pytest.mark.asyncio
async def test_add_faculty(init_db):
    faculty_name = "ИКСС"
    await add_faculty(1, faculty_name)

    async with engine.connect() as conn:
        result = (
            await conn.execute(
                select(Faculty).where(Faculty.name == faculty_name)
            )
        ).first()

    assert result.name == faculty_name


@pytest.mark.asyncio
async def test_get_all_faculties(init_db):
    faculty_names_to_add = ["ИКСС", "ИСИТ", "ЦЭУБИ"]
    for id, faculty_name in enumerate(faculty_names_to_add):
        await add_faculty(id + 1, faculty_name)

    faculties = await get_all_faculties()

    assert len(faculty_names_to_add) == len(faculties)


@pytest.mark.asyncio
async def test_get_faculty_id(init_db):
    faculty_name = "ВУЦ"
    await add_faculty(1, faculty_name)
    assert await get_faculty_id(faculty_name) == 1
