import os
import pytest

from datetime import datetime, timezone

from db import Database
from entities import TodoEntry
from persistence.errors import EntityNotFoundError, CreateError
from persistence.mapper.errors import DatabaseError
from persistence.mapper.memory import MemoryTodoEntryMapper, DatabaseTodoEntryMapper
from persistence.repository import TodoEntryRepository

_memory_storage = {
    1: TodoEntry(id=1, summary="Lorem Ipsum", created_at=datetime.now(tz=timezone.utc), tag="test")
}


class TestMemoryTodoEntryMapper:
    @pytest.mark.asyncio
    async def test_get_todo_entry(self) -> None:
        mapper = MemoryTodoEntryMapper(storage=_memory_storage)
        repository = TodoEntryRepository(mapper=mapper)

        entity = await repository.get(identifier=1)
        assert isinstance(entity, TodoEntry)

    @pytest.mark.asyncio
    async def test_todo_entry_not_found_error(self) -> None:
        mapper = MemoryTodoEntryMapper(storage=_memory_storage)
        repository = TodoEntryRepository(mapper=mapper)

        with pytest.raises(EntityNotFoundError):
            await repository.get(identifier=42)

    @pytest.mark.asyncio
    async def test_save_todo_entry(self) -> None:
        mapper = MemoryTodoEntryMapper(storage=_memory_storage)
        repository = TodoEntryRepository(mapper=mapper)

        data = TodoEntry(
            summary="Buy flowers to my wife",
            detail="We have marriage anniversary",
            created_at=datetime.now(tz=timezone.utc),
        )

        entity = await repository.create(entity=data)
        assert isinstance(entity, TodoEntry)
        assert entity.id > 1

    @pytest.mark.asyncio
    async def test_todo_entry_create_error(self) -> None:
        mapper = MemoryTodoEntryMapper(storage=None)
        repository = TodoEntryRepository(mapper=mapper)

        data = TodoEntry(
            summary="Lorem Ipsum",
            detail=None,
            created_at=datetime.now(tz=timezone.utc),
        )

        with pytest.raises(CreateError):
            await repository.create(entity=data)


class TestDatabaseTodoEntryMapper:
    @pytest.fixture
    def create_test_entry(self):
        conn, cursor = Database.get_conn(), Database.get_cursor()
        query_create_obj = """INSERT INTO Todo (summary, detail, tag, created_at) VALUES (?, ?, ?, ?);"""
        params = ("Test", "Testing", "test", "2022-12-01 12:24:03.120532+00:00")
        cursor.execute(query_create_obj, params)
        conn.commit()

    @staticmethod
    def teardown_method():
        conn, cursor = Database.get_conn(), Database.get_cursor()
        clear_table_query = """DELETE FROM Todo;"""
        cursor.execute(clear_table_query)

        reset_primary_key_query = """delete from sqlite_sequence where name = 'Todo';"""
        cursor.execute(reset_primary_key_query)
        conn.commit()

    @pytest.mark.asyncio
    async def test_get_todo_entry(self, create_test_entry) -> None:
        mapper = DatabaseTodoEntryMapper()
        repository = TodoEntryRepository(mapper=mapper)

        entity = await repository.get(identifier=1)
        assert isinstance(entity, TodoEntry)

    @pytest.mark.asyncio
    async def test_todo_entry_not_found_error(self, create_test_entry) -> None:
        mapper = DatabaseTodoEntryMapper()
        repository = TodoEntryRepository(mapper=mapper)

        with pytest.raises(EntityNotFoundError):
            await repository.get(identifier=42)

    @pytest.mark.asyncio
    async def test_save_todo_entry(self) -> None:
        mapper = DatabaseTodoEntryMapper()
        repository = TodoEntryRepository(mapper=mapper)

        data = TodoEntry(
            summary="Buy flowers to my wife",
            detail="We have marriage anniversary",
            created_at=datetime.now(tz=timezone.utc),
        )

        entity = await repository.create(entity=data)
        assert isinstance(entity, TodoEntry)
        assert entity.id == 1

    @pytest.mark.asyncio
    async def test_todo_entry_create_error(self) -> None:
        mapper = DatabaseTodoEntryMapper()
        repository = TodoEntryRepository(mapper=mapper)

        data = TodoEntry(
            summary="Lorem Ipsum",
            created_at=datetime.now(tz=timezone.utc),
        )

        conn = Database.get_conn()
        conn.close()
        with pytest.raises(DatabaseError):
            await repository.create(entity=data)

        Database.initialize("test.db")
