"""
Event Bot Server
"""

import enum
from typing import Optional, Tuple, Union


class Direction(enum.IntEnum):
    BEFORE = -1
    AROUND = 0
    AFTER = 1


class Listing:
    """Listing class.
    Methods for working with listings queries.
    """

    def __init__(self, min_limit: int, max_limit: int, default_limit: int):
        self.min_limit = min_limit
        self.max_limit = max_limit

        if self.validate_limit(default_limit) != default_limit:
            raise ValueError("Your default limit value does not comply with "
                             "the min and max value requirements.")

        self.default_limit = default_limit

    def validate_limit(self, limit: Optional[Union[int, str]]=None) -> int:
        """Returns validated limit value.
        Limit value should comply with the min and max value
        requirements.
        """
        if limit is None:
            return self.default_limit

        if isinstance(limit, str):
            limit = int(limit)

        return max(self.min_limit, min(self.max_limit, limit))

    @staticmethod
    def validate_id(id: Union[int, str]) -> Optional[int]:
        """Returns validated ID."""
        if isinstance(id, str):
            id = int(id)

        if 0 <= id:
            return id
        return None

    def validate(self,
                 before: Optional[Union[int, str]]=None,
                 after: Optional[Union[int, str]]=None,
                 limit: Optional[Union[int, str]]=None
                 ) -> Tuple[Optional[int], int, Direction]:
        """Validate a listing query values.
        Returns a ID of thing, from  which to search, and the correct
        value of limit. If neither of `before` and `after` is
        specified, returns None as ID of thing and `after`, that means
        to search from start of the list of things.
        """
        limit = self.validate_limit(limit)

        if before and after:
            raise ValueError("Only one of `before` and `after` arguments must "
                             "be specified")

        if before is not None:
            return self.validate_id(before), limit, Direction.BEFORE
        if after is not None:
            return self.validate_id(after), limit, Direction.AFTER

        return None, limit, Direction.AFTER

    def validate_from_request(self, request):
        """Validate a listing query values from the request instance."""
        return self.validate(request.raw_args.get("before", None),
                             request.raw_args.get("after", None),
                             request.raw_args.get("limit", None))
