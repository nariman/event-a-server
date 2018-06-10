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
    "users",
    metadata,

    sa.Column("id", GUID, primary_key=True, default=uuid.uuid4),

    sa.Column("created_at", DateTime, default=pendulum.now, nullable=False)
)


def json_format(user):
    """Returns JSON-ready representation of the user object."""
    return {
        # convert uuid to str
        "id": str(user["id"]),

        # convert datetimes to iso8601 format
        "created_at": user["created_at"].isoformat()
    }
