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


class EventController(HTTPMethodView):

    @helpers.db_connections.provide_connection()
    async def get(self, request, event_id, connection):
        """Returns an event."""

        # Prepare query
        query = (select([models.event.t])
            .select_from(models.event.t)
            .where(models.event.t.c.id == event_id))

        # Compile query, execute and parse
        query, params = asyncpgsa.compile_query(query)
        try:
            try:
                row = await connection.fetchrow(query, *params)
            except PostgresError:
                raise exceptions.NotFetchedError

            if not row:
                raise exceptions.NotFoundError
        except exceptions.NotFoundError:
            return response.json(
                response_wrapper.error("Event not found"),
                status=404)

        event = models.event.json_format(models.event.t.parse(row))

        # Return the event
        return response.json(response_wrapper.ok(event))
