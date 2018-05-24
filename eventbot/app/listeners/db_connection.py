"""
Event Bot Server
"""

import asyncpg

from eventbot.app import state
from eventbot.config import db as config


async def before_start_listener(app, loop):
    """Creates a connection pool."""
    state.pool = await asyncpg.create_pool(
        host=config.HOST,
        port=config.PORT,
        user=config.USER,
        password=config.PASSWORD,
        database=config.DATABASE,
        min_size=config.POOL_MIN_SIZE,
        max_size=config.POOL_MAX_SIZE,
        max_queries=config.MAX_QUERIES,
        max_inactive_connection_lifetime=config.MAX_INACTIVE_CONNECTION_LIFETIME,
        loop=loop)


async def after_stop_listener(app, loop):
    """Closes the connection pool."""
    await state.pool.close()
