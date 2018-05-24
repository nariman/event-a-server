"""
Event Bot Server
"""

import asyncio

import asyncpg
import asyncpg.pool
from sanic import Sanic


# Event loop configuration

loop = asyncio.get_event_loop()


# Application instance

app = Sanic()


# PostgreSQL connection pool

pool: asyncpg.pool.Pool
"""PostgreSQL connection pool."""
