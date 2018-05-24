"""
Event Bot Server
"""

from datetime import datetime

import pendulum
import sqlalchemy as sa


class DateTime(sa.TypeDecorator):
    """DateTime with a default UTC timezone.

    Implements a type with explicit requirement to set timezones.
    Before saving to a database, converts it to the UTC timezone.
    After retrieving from a database, has the UTC timezone.
    """
    impl = sa.DateTime(timezone=True)

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not isinstance(value, datetime):
                raise TypeError("Expected datetime.datetime, not " +
                                repr(value))
            elif value.tzinfo is None:
                raise ValueError("Naive datetime is disallowed")
            return value.astimezone(pendulum.UTC)

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=pendulum.UTC)
        return value
