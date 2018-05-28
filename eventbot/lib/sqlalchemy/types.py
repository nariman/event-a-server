"""
Event Bot Server
"""

import uuid
from datetime import datetime

import pendulum
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


class GUID(sa.TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    String(32), storing as stringified hex values.
    """
    impl = sa.String

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(sa.String(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


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
