import pytest
from sqlalchemy import select

from app.db.admins import (
    Admin,
    add_admin,
    delete_admin,
    get_all_admins,
    get_all_superusers,
    get_admin_by_id,
)
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


@pytest.mark.asyncio
async def test_delete_admin(init_db):
    await add_admin(1, True, None)
    await add_admin(2, False, 1)

    await delete_admin(1)
    assert len(await get_all_admins()) == 1


@pytest.mark.asyncio
async def test_get_admin_by_id(init_db):
    await add_admin(1, True, None)
    await add_admin(22, False, 1)

    admin_by_id = await get_admin_by_id(22)

    assert (
        admin_by_id.id == 22
        and not admin_by_id.is_superuser
        and admin_by_id.faculty_id == 1
    )
