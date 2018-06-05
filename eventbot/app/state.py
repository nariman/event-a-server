"""
Event Bot Server
"""

import asyncio
import typing

import asyncpg
import asyncpg.pool
from sanic import Sanic
from sanic_prometheus import monitor

from eventbot.lib import snowflake


# Event loop configuration

loop = asyncio.get_event_loop()


# Application instance

app = Sanic()

monitor(app).expose_endpoint()


# PostgreSQL connection pool

pool: asyncpg.pool.Pool
"""PostgreSQL connection pool."""
