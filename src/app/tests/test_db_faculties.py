import pytest
from sqlalchemy import select

from app.db.common import engine
from app.db.faculties import (
    Faculty,
    add_faculty,
    get_faculty_id,
    get_faculty_name,
)


@pytest.mark.asyncio
async def test_add_faculty(init_db):
    faculty_name = "ВУЦ"
    await add_faculty(4, faculty_name)

    async with engine.connect() as conn:
        result = (
            await conn.execute(
                select(Faculty).where(Faculty.name == faculty_name)
            )
        ).first()

    assert result.name == faculty_name

@pytest.mark.asyncio
async def test_get_faculty_id(init_db):
    faculty_name = "ВУЦ"
    await add_faculty(4, faculty_name)
    assert await get_faculty_id(faculty_name) == 4


@pytest.mark.asyncio
async def test_get_faculty_name(init_db):
    faculty_id = 3
    await add_faculty(faculty_id, "ИСиТ")
    faculty_name = await get_faculty_name(faculty_id)
    assert faculty_name == "ИСиТ"
