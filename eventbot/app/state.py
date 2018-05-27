"""
Event Bot Server
"""

import asyncio
import typing

import asyncpg
import asyncpg.pool
from sanic import Sanic

from eventbot.lib import snowflake


# Event loop configuration

loop = asyncio.get_event_loop()


# Application instance

app = Sanic()


# PostgreSQL connection pool

pool: asyncpg.pool.Pool
"""PostgreSQL connection pool."""


# Snowflake ID generator

snowflake_generator = snowflake.generator(0)
