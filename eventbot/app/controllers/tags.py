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
from sqlalchemy.sql.expression import func

from eventbot.app import models
from eventbot.app import helpers
from eventbot.lib import exceptions
from eventbot.lib import listing
from eventbot.lib import response_wrapper


class TagsController(HTTPMethodView):

    @helpers.db_connections.provide_connection()
    async def get(self, request, event_id, connection):
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

        query = (select([models.tag.t])
            .select_from(models.tag.t)
            .where(models.tag.t.c.event_id == event["id"])
            .order_by(models.tag.t.c.name.asc())
            .order_by(models.tag.t.c.id.desc())
            .apply_labels())

        query, params = asyncpgsa.compile_query(query)

        try:
            rows = await connection.fetch(query, *params)
        except PostgresError:
            raise exceptions.NotFetchedError

        tags = [
            models.tag.t.parse(row, prefix="tags_")
            for row in rows
        ]

        for tag in tags:
            tag["id"] = str(tag["id"])
            tag["event_id"] = str(tag["event_id"])

        return response.json(response_wrapper.ok(tags))

    @helpers.db_connections.provide_connection()
    async def post(self, request, event_id, connection):
        tag = request.json

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

                tag = models.tag.t.parse(row, prefix="tags_")
            except (PostgresError, exceptions.DatabaseError):
                raise exceptions.NotCreatedError

        tag["id"] = str(tag["id"])
        tag["event_id"] = str(tag["event_id"])

        return response.json(response_wrapper.ok(tag), status=201)
