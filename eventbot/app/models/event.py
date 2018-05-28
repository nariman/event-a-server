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
    "events",
    metadata,

    sa.Column("id", GUID, primary_key=True, default=uuid.uuid4),

    sa.Column("name", sa.String(1024), nullable=False),
    sa.Column("description", sa.Text(), nullable=False),

    sa.Column("start_date", sa.Date, nullable=False),
    sa.Column("end_date", sa.Date, nullable=False),

    sa.Column("created_at", DateTime, default=pendulum.now, nullable=False)
)
