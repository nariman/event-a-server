"""
Event Bot Server
"""

from jose.exceptions import JWTError


class EventBotError(Exception):
    pass


class AuthenticationError(EventBotError):
    pass


class ValidationError(EventBotError, ValueError):
    pass


class JWTError(EventBotError, JWTError):
    pass


class DatabaseError(EventBotError):
    pass


class NotFetchedError(DatabaseError):
    pass


class NotFoundError(DatabaseError):
    pass


class NotSavedError(DatabaseError):
    pass


class NotCreatedError(NotSavedError):
    pass


class NotUpdatedError(NotSavedError):
    pass
