import os
import pytest

from db import Database


@pytest.fixture(autouse=True, scope="session")
def init_test_db():
    Database.initialize("test.db")

    yield

    os.unlink("test.db")
