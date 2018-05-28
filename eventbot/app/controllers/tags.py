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


class TagsController(HTTPMethodView):

    @helpers.db_connections.provide_connection()
    async def get(self, request, event_id, connection):
        """Returns a list of event tags."""

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

        # If event exists, query all tags
        query = (select([models.tag.t])
            .select_from(models.tag.t)
            .where(models.tag.t.c.event_id == event["id"])
            .order_by(models.tag.t.c.name.asc())
            .order_by(models.tag.t.c.id.desc())
            .apply_labels())

        # Compile query, execute and parse
        query, params = asyncpgsa.compile_query(query)
        try:
            rows = await connection.fetch(query, *params)
        except PostgresError:
            raise exceptions.NotFetchedError

        tags = [
            models.tag.json_format(models.tag.t.parse(row, prefix="tags_"))
            for row in rows
        ]

        # Return the list
        return response.json(response_wrapper.ok(tags))

    @helpers.db_connections.provide_connection()
    async def post(self, request, event_id, connection):
        """Creates a new event tag."""

        # Tag form
        tag = request.json

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
        # We need to 1) save tag, 2) fetch tag from a database
        async with connection.transaction():
            try:
                query = (models.tag.t
                    .insert()
                    .values(event_id=event["id"],
                            name=tag["name"],
                            color=tag["color"])
                    .returning(models.tag.t.c.id))
                query, params = asyncpgsa.compile_query(query)

                id = await connection.fetchval(query, *params)

                query = (select([models.tag.t])
                    .select_from(models.tag.t)
                    .where(models.tag.t.c.id == id)
                    .apply_labels())
                query, params = asyncpgsa.compile_query(query)

                try:
                    row = await connection.fetchrow(query, *params)
                except PostgresError:
                    raise exceptions.NotFetchedError

                if not row:
                    raise exceptions.NotFoundError

                tag = models.tag.json_format(
                    models.tag.t.parse(row, prefix="tags_"))
            except (PostgresError, exceptions.DatabaseError):
                raise exceptions.NotCreatedError

        return response.json(response_wrapper.ok(tag), status=201)
