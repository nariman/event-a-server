"""
Event Bot Server
"""

import asyncpg
import sqlalchemy as sa

from eventbot.app import state


def get_pool():
    """Returns a database pool."""
    return state.pool


def parse(table: sa.Table, record: asyncpg.Record, prefix: str="") -> dict:
    """Parses an :class:`asyncpg.Record` object into dict."""
    parsed = {column.key: None for column in self.columns}

    for key in parsed:
        if prefix + key in record:
            parsed[key] = record[prefix + key]

    return parsed


def get_connection():
    """Returns a database connection.

    Don't forget to close (return) the acquired connection."""
    return await (get_pool().acquire())


def close_connection(connection: asyncpg.Connection):
    """Closes an acquired connection."""
    await (get_pool().release(connection))


def provide_connection(key="connection", force_replace=False):
    """An easy way to get the instance of database connection.

    Pass `force_replace=True` if you want to replace already provided
    connection with a new one."""
    def decorator(fn):
        async def wrapper(*args, **kwargs):
            if force_replace or key not in kwargs:
                async with get_pool().acquire() as conn:
                    kwargs[key] = conn
                    return await fn(*args, **kwargs)
            return await fn(*args, **kwargs)

        return wrapper
    return decorator
