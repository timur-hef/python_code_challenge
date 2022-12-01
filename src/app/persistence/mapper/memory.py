from random import randint

from db import Database
from entities import TodoEntry
from persistence.mapper.errors import EntityNotFoundMapperError, CreateMapperError, DatabaseError
from persistence.mapper.interfaces import TodoEntryMapperInterface


class MemoryTodoEntryMapper(TodoEntryMapperInterface):
    _storage: dict

    def __init__(self, storage: dict) -> None:
        self._storage = storage

    async def get(self, identifier: int) -> TodoEntry:
        try:
            return self._storage[identifier]
        except KeyError:
            raise EntityNotFoundMapperError(f"Entity `id:{identifier}` was not found.")

    async def create(self, entity: TodoEntry) -> TodoEntry:
        try:
            entity.id = self._generate_unique_id()
            self._storage[entity.id] = entity
            return entity
        except TypeError as error:
            raise CreateMapperError(error)

    def _generate_unique_id(self) -> int:
        identifier = randint(1, 10_000)
        while identifier in self._storage:
            identifier = randint(1, 10_000)

        return identifier


class DatabaseTodoEntryMapper(TodoEntryMapperInterface):
    def __init__(self) -> None:
        self._cursor = Database.get_cursor()
        self._conn = Database.get_conn()

    async def get(self, identifier: int) -> TodoEntry:
        try:
            query = """SELECT * FROM Todo WHERE id = ?;"""
            params = identifier,
            self._cursor.execute(query, params)
            result = self._cursor.fetchone()
        except Exception as e:
            raise DatabaseError(f"Unknown error occurred when app was trying to fetch results from the database: \n{e}")

        if result is None:
            raise EntityNotFoundMapperError(f"Entity `id:{identifier}` was not found.")

        return TodoEntry(id=result[0], summary=result[1], detail=result[2], created_at=result[3], tag=result[4])

    async def create(self, entity: TodoEntry) -> TodoEntry:
        try:
            query = """INSERT INTO Todo (summary, detail, tag, created_at) VALUES (?, ?, ?, ?);"""
            params = (
                getattr(entity, "summary"),
                getattr(entity, "detail", None),
                getattr(entity, "tag", None),
                getattr(entity, "created_at")
            )
            self._cursor.execute(query, params)

            query = """SELECT id FROM Todo WHERE id = (SELECT MAX(id) from Todo)"""
            self._cursor.execute(query)
            entity.id = self._cursor.fetchone()[0]

            self._conn.commit()
        except Exception as e:
            raise DatabaseError(f"Unknown error occurred when app was trying to insert data to the database: \n{e}")

        return entity
