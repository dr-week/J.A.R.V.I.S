import os
import pytest
import pytest_asyncio
from sqlmodel import SQLModel, Field
from backend.plugins.database import init_db, get_session, create, read

class DatabaseItem(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

@pytest_asyncio.fixture(scope="module")
async def db_path(tmp_path_factory):
    db_file = tmp_path_factory.mktemp("db_test") / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_file}"
    await init_db()
    return db_file

@pytest.mark.asyncio
async def test_create_and_read(db_path):
    async for session in get_session():
        item = DatabaseItem(name="sample")
        created = await create(session, item)
        assert created.id is not None
        fetched = await read(session, DatabaseItem, DatabaseItem.id == created.id)
        assert fetched is not None
        assert fetched.name == "sample"
