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


def json_format(event):
    """Returns JSON-ready representation of the event object."""
    return {
        # convert uuid to str
        "id": str(event["id"]),

        # name and description as is
        "name": event["name"],
        "description": event["description"],

        # convert datetimes to iso8601 format
        "start_date": event["start_date"].isoformat(),
        "end_date": event["end_date"].isoformat(),
        "created_at": event["created_at"].isoformat()
    }
