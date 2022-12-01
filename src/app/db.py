import sqlite3


class Database:
    __conn = None
    __cursor = None

    @classmethod
    def initialize(cls, db_uri):
        cls.__conn = sqlite3.connect(db_uri)
        cls.__cursor = cls.__conn.cursor()

        cls.__cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Todo (
                        id integer primary key AUTOINCREMENT NOT NULL,
                        summary varchar(26) NOT NULL,
                        detail varchar(255),
                        created_at varchar(255) NOT NULL,
                        tag varchar(255)
                    );
                """)
        cls.__conn.commit()

    @classmethod
    def get_cursor(cls):
        return cls.__cursor

    @classmethod
    def get_conn(cls):
        return cls.__conn
