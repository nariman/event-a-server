"""
Event Bot Server
"""

import datetime

import pendulum
import sqlalchemy as sa

from . import metadata
from eventbot.lib.sqlalchemy.base import Table
from eventbot.lib.sqlalchemy.types import DateTime


t = table = Table(
    "events",
    metadata,

    sa.Column("id", sa.BigInteger, primary_key=True),

    sa.Column("name", sa.String(1024), nullable=False),
    sa.Column("description", sa.Text(), nullable=False),

    sa.Column("start_time", DateTime,
              default=lambda: datetime.utcnow().replace(tzinfo=pendulum.UTC),
              nullable=False),
    sa.Column("end_time", DateTime,
              default=lambda: datetime.utcnow().replace(tzinfo=pendulum.UTC),
              nullable=False),

    sa.Column("created_at", DateTime,
              default=lambda: datetime.utcnow().replace(tzinfo=pendulum.UTC),
              nullable=False)
)
