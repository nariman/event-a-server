"""
Event Bot Server
"""

import datetime

import pendulum
import sqlalchemy as sa

from . import metadata
from eventbot.lib.sqlalchemy.types import DateTime


t = table = sa.Table(
    "tags",
    metadata,

    sa.Column("id", sa.BigInteger, primary_key=True),
    sa.Column("event_id", sa.BigInteger, nullable=False),

    sa.Column("name", sa.String(1024), nullable=False),
    sa.Column("color", sa.String(8), nullable=False),
)
