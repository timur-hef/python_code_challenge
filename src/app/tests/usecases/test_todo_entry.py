from datetime import datetime, timezone

import pytest

from entities import TodoEntry
from persistence.mapper.memory import MemoryTodoEntryMapper
from persistence.repository import TodoEntryRepository
from usecases import get_todo_entry, NotFoundError, create_todo_entry, UseCaseError


class Base:
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


class TestGetTodo(Base):
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


class TestPostTodo(Base):
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
