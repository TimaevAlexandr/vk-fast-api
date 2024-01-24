import pytest
from sqlalchemy import select

from app.db.admins import Admin, add_admin, get_all_admins, get_all_superusers
from app.db.common import engine


@pytest.mark.asyncio
async def test_add_admin(init_db):
    id = 4
    is_superuser = True
    faculty_id = 4

    await add_admin(id, is_superuser, faculty_id)

    async with engine.connect() as conn:
        result = (
            await conn.execute(
                select(Admin).where(Admin.faculty_id == faculty_id)
            )
        ).first()

    assert result.is_superuser == is_superuser
    assert result.faculty_id == faculty_id


@pytest.mark.asyncio
async def test_get_all_admins(init_db):
    faculty_ids_to_add = [1, 2, 3]
    for admin_id, faculty_id in enumerate(faculty_ids_to_add):
        await add_admin(admin_id + 1, False, faculty_id)

    admins = await get_all_admins()

    assert len(admins) == len(faculty_ids_to_add)


@pytest.mark.asyncio
async def test_get_all_superusers(init_db):
    await add_admin(1, True, 0)  # create superadmin
    await add_admin(2, False, 1)  # create admin
    superusers = await get_all_superusers()

    assert len(superusers) == 1
