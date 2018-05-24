"""
Event Bot Server
"""

import asyncpgsa
from asyncpg.connection import Connection
from asyncpg.exceptions import PostgresError
from sanic import response
from sanic.views import HTTPMethodView
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import func

from eventbot.app import models
from eventbot.app import helpers
from eventbot.lib import exceptions
from eventbot.lib import listing
from eventbot.lib import response_wrapper


class EventsController(HTTPMethodView):

    default_listing = listing.Listing(1, 100, 25)

    @helpers.db_connections.provide_connection()
    async def get(self, request, connection):
        try:
            pivot, limit, direction = \
                self.default_listing.validate_from_request(request)
        except ValueError:
            return response.json(
                response_wrapper.error("Listing arguments error"), status=400)

        query = (select([models.event.t])
            .select_from(models.event.t)
            .apply_labels())

        query = query.order_by(models.event.t.c.id.desc())

        if pivot is not None:
            try:
                query_pivot = query.where(models.event.t.c.id == pivot)
                query_pivot, params = asyncpgsa.compile_query(query_pivot)

                try:
                    row = await connection.fetchrow(query_pivot, *params)
                except PostgresError:
                    raise exceptions.NotFetchedError

                if not row:
                    raise exceptions.NotFoundError

                pivot = models.event.t.parse(row, prefix="events_")
            except exceptions.NotFoundError:
                return response.json(
                    response_wrapper.error("Pivot event not found"),
                    status=400)

            if direction == listing.Direction.BEFORE:
                query = query.where(models.event.t.c.id > pivot["id"])
            elif direction == listing.Direction.AFTER:
                query = query.where(models.event.t.c.id < pivot["id"])

        query = query.limit(limit)
        query, params = asyncpgsa.compile_query(query)

        try:
            rows = await connection.fetch(query, *params)
        except PostgresError:
            raise exceptions.NotFetchedError

        events = [models.event.t.parse(row, prefix="events_") for row in rows]
        return response.json(response_wrapper.ok(events))
