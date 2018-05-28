"""
Event Bot Server
"""

import asyncpgsa
from asyncpg.connection import Connection
from asyncpg.exceptions import PostgresError
from sanic import response
from sanic.views import HTTPMethodView
from sqlalchemy.sql import select

from eventbot.app import models
from eventbot.app import helpers
from eventbot.lib import exceptions
from eventbot.lib import response_wrapper


class LocationsController(HTTPMethodView):

    @helpers.db_connections.provide_connection()
    async def get(self, request, event_id, connection):
        """Returns a list of event locations."""

        # Check, is event exists
        try:
            query_event = (select([models.event.t])
                .select_from(models.event.t)
                .where(models.event.t.c.id == event_id)
                .apply_labels())
            query_event, params = asyncpgsa.compile_query(query_event)

            try:
                row = await connection.fetchrow(query_event, *params)
            except PostgresError:
                raise exceptions.NotFetchedError

            if not row:
                raise exceptions.NotFoundError

            event = models.event.t.parse(row, prefix="events_")
        except exceptions.NotFoundError:
            return response.json(
                response_wrapper.error("Event not found"),
                status=404)

        # If event exists, query all locations
        query = (select([models.location.t])
            .select_from(models.location.t)
            .where(models.location.t.c.event_id == event["id"])
            .order_by(models.location.t.c.name.asc())
            .order_by(models.location.t.c.id.desc())
            .apply_labels())

        # Compile query, execute and parse
        query, params = asyncpgsa.compile_query(query)
        try:
            rows = await connection.fetch(query, *params)
        except PostgresError:
            raise exceptions.NotFetchedError

        locations = [
            models.location.json_format(models.location.t.parse(row, prefix="locations_"))
            for row in rows
        ]

        # Return the list
        return response.json(response_wrapper.ok(locations))

    @helpers.db_connections.provide_connection()
    async def post(self, request, event_id, connection):
        """Creates a new event location."""

        # Location form
        location = request.json

        # Check, is event exists
        try:
            query_event = (select([models.event.t])
                .select_from(models.event.t)
                .where(models.event.t.c.id == event_id)
                .apply_labels())
            query_event, params = asyncpgsa.compile_query(query_event)

            try:
                row = await connection.fetchrow(query_event, *params)
            except PostgresError:
                raise exceptions.NotFetchedError

            if not row:
                raise exceptions.NotFoundError

            event = models.event.t.parse(row, prefix="events_")
        except exceptions.NotFoundError:
            return response.json(
                response_wrapper.error("Event not found"),
                status=404)

        # If event exists, create a transaction
        # We need to 1) save location, 2) fetch location from a database
        async with connection.transaction():
            try:
                query = (models.location.t
                    .insert()
                    .values(event_id=event["id"],
                            name=location["name"])
                    .returning(models.location.t.c.id))
                query, params = asyncpgsa.compile_query(query)

                id = await connection.fetchval(query, *params)

                query = (select([models.location.t])
                    .select_from(models.location.t)
                    .where(models.location.t.c.id == id)
                    .apply_labels())
                query, params = asyncpgsa.compile_query(query)

                try:
                    row = await connection.fetchrow(query, *params)
                except PostgresError:
                    raise exceptions.NotFetchedError

                if not row:
                    raise exceptions.NotFoundError

                location = models.location.json_format(
                    models.location.t.parse(row, prefix="locations_"))
            except (PostgresError, exceptions.DatabaseError):
                raise exceptions.NotCreatedError

        return response.json(response_wrapper.ok(location), status=201)
