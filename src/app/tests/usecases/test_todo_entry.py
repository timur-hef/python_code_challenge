import pytest

from datetime import datetime, timezone

from db import Database
from entities import TodoEntry
from persistence.mapper.memory import MemoryTodoEntryMapper, DatabaseTodoEntryMapper
from persistence.repository import TodoEntryRepository
from usecases import get_todo_entry, NotFoundError, create_todo_entry, UseCaseError


class BaseMemoryMapper:
    _storage = {
        1: TodoEntry(id=1, summary="Lorem Ipsum", created_at=datetime.now(tz=timezone.utc))
    }
    mapper = MemoryTodoEntryMapper(storage=_storage)
    repository = TodoEntryRepository(mapper=mapper)

    @pytest.fixture
    def no_storage(self):
        self.mapper = MemoryTodoEntryMapper(None)
        self.repository = TodoEntryRepository(mapper=self.mapper)

        yield

        self.mapper = MemoryTodoEntryMapper(self._storage)
        self.repository = TodoEntryRepository(mapper=self.mapper)


class TestGetTodo(BaseMemoryMapper):
    @pytest.mark.asyncio
    async def test_get_todo_entry(self) -> None:
        entity = await get_todo_entry(identifier=1, repository=self.repository)

        assert entity.id == self._storage[1].id
        assert entity.summary == self._storage[1].summary
        assert entity.created_at == self._storage[1].created_at
        assert entity.tag == self._storage[1].tag

    @pytest.mark.asyncio
    async def test_get_not_existing_todo_entry(self) -> None:
        with pytest.raises(NotFoundError):
            await get_todo_entry(identifier=42, repository=self.repository)


class TestPostTodo(BaseMemoryMapper):
    @pytest.mark.asyncio
    async def test_create_todo_entry(self) -> None:
        data = TodoEntry(summary="Lorem ipsum", created_at=datetime.now(tz=timezone.utc), tag="test")
        entity = await create_todo_entry(entity=data, repository=self.repository)

        assert entity.summary == data.summary
        assert entity.created_at == data.created_at
        assert entity.tag == data.tag

    @pytest.mark.asyncio
    async def test_todo_entry_creation_error(self, no_storage) -> None:
        data = TodoEntry(summary="Lorem ipsum", created_at=datetime.now(tz=timezone.utc), tag="test")
        with pytest.raises(UseCaseError):
            await create_todo_entry(entity=data, repository=self.repository)


class BaseDatabaseMapper:
    @staticmethod
    @pytest.fixture
    def init_repository():
        mapper = DatabaseTodoEntryMapper()
        repository = TodoEntryRepository(mapper=mapper)

        yield repository

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


class TestGetTodoDatabase(BaseDatabaseMapper):
    @pytest.mark.asyncio
    async def test_get_todo_entry(self, init_repository, create_test_entry) -> None:
        entity = await get_todo_entry(identifier=1, repository=init_repository)

        assert entity.id == 1
        assert entity.summary == "Test"
        assert entity.detail == "Testing"
        assert entity.created_at == datetime(2022, 12, 1, 12, 24, 3, 120532, tzinfo=timezone.utc)
        assert entity.tag == "test"

    @pytest.mark.asyncio
    async def test_get_not_existing_todo_entry(self, init_repository) -> None:
        with pytest.raises(NotFoundError):
            await get_todo_entry(identifier=42, repository=init_repository)


class TestPostTodoDatabase(BaseDatabaseMapper):
    @pytest.mark.asyncio
    async def test_create_todo_entry(self, init_repository) -> None:
        data = TodoEntry(
            summary="Lorem ipsum",
            created_at=datetime(2022, 12, 1, 12, 24, 3, 120532, tzinfo=timezone.utc),
            tag="test"
        )
        entity = await create_todo_entry(entity=data, repository=init_repository)

        assert entity.summary == "Lorem ipsum"
        assert entity.detail is None
        assert entity.created_at == datetime(2022, 12, 1, 12, 24, 3, 120532, tzinfo=timezone.utc)
        assert entity.tag == "test"
        assert entity.id == 1

    @pytest.mark.asyncio
    async def test_todo_entry_creation_error(self, init_repository) -> None:
        data = TodoEntry(summary="Lorem ipsum", created_at=datetime.now(tz=timezone.utc), tag="test")
        conn = Database.get_conn()
        conn.close()
        with pytest.raises(UseCaseError):
            await create_todo_entry(entity=data, repository=init_repository)

        Database.initialize("test.db")
