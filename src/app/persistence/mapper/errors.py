class MapperError(Exception):
    pass


class EntityNotFoundMapperError(MapperError):
    pass


class CreateMapperError(MapperError):
    pass


class DatabaseError(MapperError):
    pass
