"""
Event Bot Server
"""

import datetime

import pendulum
import sqlalchemy as sa

from . import metadata
from eventbot.lib.sqlalchemy.base import Table
from eventbot.lib.sqlalchemy.types import DateTime, GUID


t = table = Table(
    "user_platforms",
    metadata,

    sa.Column("user_id", GUID, nullable=False),
    sa.Column("platform_id", GUID, nullable=False),

    sa.Column("user_platform_id", sa.String(1024)),
    sa.Column("created_at", DateTime, default=pendulum.now, nullable=False)
)


def json_format(user_platform):
    """Returns JSON-ready representation of the user's platform
    object."""
    return {
        # convert uuid to str
        "user_id": str(user_platform["user_id"]),
        "platform_id": str(user_platform["platform_id"]),

        # unknown id as is
        "user_platform_id": user_platform["user_platform_id"],

        # convert datetimes to iso8601 format
        "created_at": user_platform["created_at"].isoformat()
    }
