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


def json_format(session):
    """Returns JSON-ready representation of the session object."""
    return {
        # convert uuid to str
        "id": str(session["id"]),
        # convert uuid to str, w/o/ event object
        "event_id": str(session["event_id"]),

        # title and description as is
        "title": session["title"],
        "description": session["description"],

        # convert datetimes to iso8601 format
        "start_time": session["start_time"].isoformat(),
        "end_time": session["end_time"].isoformat(),
        "created_at": session["created_at"].isoformat()
    }
