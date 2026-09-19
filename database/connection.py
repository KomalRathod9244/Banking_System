from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2.extensions import connection, cursor

from config.settings import settings


@contextmanager
def get_connection() -> Generator[connection, None, None]:
    conn = psycopg2.connect(**settings.get_connection_params())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def get_cursor() -> Generator[tuple[connection, cursor], None, None]:
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            yield conn, cur
        finally:
            cur.close()