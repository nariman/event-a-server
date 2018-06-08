"""
Event Bot Server
"""

import asyncpgsa
import pendulum
from asyncpg.connection import Connection
from asyncpg.exceptions import PostgresError
from sanic import response
from sanic.views import HTTPMethodView
from sqlalchemy.sql import select

from eventbot.app import models
from eventbot.app import helpers
from eventbot.lib import exceptions
from eventbot.lib import listing
from eventbot.lib import response_wrapper


class EventsController(HTTPMethodView):

    default_listing = listing.Listing(1, 100, 25)
    """Limits and default options for events listing."""

    @helpers.db_connections.provide_connection()
    async def get(self, request, connection):
        """Returns a list of events."""

        # Validate listing
        try:
            pivot, limit, direction = \
                self.default_listing.validate_from_request(request)
        except ValueError:
            return response.json(
                response_wrapper.error("Listing arguments error"), status=400)

        # Prepare query
        query = (select([models.event.t])
            .select_from(models.event.t)
            .apply_labels())

        # Adjust query according to listing options
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
                query = (query
                    .where(models.event.t.c.start_date >= pivot["start_date"])
                    .where(models.event.t.c.end_date >= pivot["end_date"])
                    .where(models.event.t.c.created_at >= pivot["created_at"])
                    .where(models.event.t.c.id < pivot["id"]))
            elif direction == listing.Direction.AFTER:
                query = (query
                    .where(models.event.t.c.start_date <= pivot["start_date"])
                    .where(models.event.t.c.end_date <= pivot["end_date"])
                    .where(models.event.t.c.created_at <= pivot["created_at"])
                    .where(models.event.t.c.id > pivot["id"]))

        # Apply sorting and limit
        query = (query
            .order_by(models.event.t.c.start_date.desc())
            .order_by(models.event.t.c.end_date.asc())
            .order_by(models.event.t.c.created_at.asc())
            .order_by(models.event.t.c.id.desc())
            .limit(limit))

        # Compile query, execute and parse
        query, params = asyncpgsa.compile_query(query)
        try:
            rows = await connection.fetch(query, *params)
        except PostgresError:
            raise exceptions.NotFetchedError

        events = [
            models.event.json_format(models.event.t.parse(row, prefix="events_"))
            for row in rows
        ]

        # Return the list
        return response.json(response_wrapper.ok(events))

    @helpers.db_connections.provide_connection()
    async def post(self, request, connection):
        """Creates a new event."""

        # Event form
        event = request.json

        # Create a transaction
        # We need to 1) save event, 2) fetch event from a database
        async with connection.transaction():
            try:
                query = (models.event.t
                    .insert()
                    .values(name=event["name"],
                            description=event["description"],
                            start_date=pendulum.parse(event["start_date"]),
                            end_date=pendulum.parse(event["end_date"]))
                    .returning(models.event.t.c.id))
                query, params = asyncpgsa.compile_query(query)

                id = await connection.fetchval(query, *params)

                query = (select([models.event.t])
                    .select_from(models.event.t)
                    .where(models.event.t.c.id == id)
                    .apply_labels())
                query, params = asyncpgsa.compile_query(query)

                try:
                    row = await connection.fetchrow(query, *params)
                except PostgresError:
                    raise exceptions.NotFetchedError

                if not row:
                    raise exceptions.NotFoundError

                event = models.event.json_format(
                    models.event.t.parse(row, prefix="events_"))
            except (PostgresError, exceptions.DatabaseError):
                raise exceptions.NotCreatedError

        return response.json(response_wrapper.ok(event), status=201)
