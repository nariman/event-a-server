"""
Event Bot Server
"""

import datetime
import uuid

import pendulum
import sqlalchemy as sa

from . import metadata
from eventbot.lib.sqlalchemy.base import Table
from eventbot.lib.sqlalchemy.types import DateTime, GUID


t = table = Table(
    "sessions",
    metadata,

    sa.Column("id", GUID, primary_key=True, default=uuid.uuid4),
    sa.Column("event_id", GUID, nullable=False),

    sa.Column("title", sa.String(1024), nullable=False),
    sa.Column("description", sa.Text(), nullable=False),

    sa.Column("start_time", DateTime, nullable=False),
    sa.Column("end_time", DateTime, nullable=False),

    sa.Column("created_at", DateTime, default=pendulum.now, nullable=False)
)
