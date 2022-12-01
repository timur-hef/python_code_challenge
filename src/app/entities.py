from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AbstractEntity(BaseModel):
    id: Optional[int]


class TodoEntry(AbstractEntity):
    summary: str
    detail: Optional[str]
    created_at: datetime
    tag: Optional[str]


result = {
    "id": 1,
    "summary": 'Fuck off',
    "detail": 'What the fuck',
    "created_at": '1970-01-01 00:00:01+00:00',
    "tag": 'some new one'
}

td = TodoEntry(id=1, summary="sdf", created_at="1970-01-01 00:00:01+00:00")

print(td)