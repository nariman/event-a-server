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


class ScheduleItemsController(HTTPMethodView):

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

        query = (select([models.schedule_item.t])
            .select_from(models.schedule_item.t)
            .where(models.schedule_item.t.c.event_id == event["id"])
            .order_by(models.schedule_item.t.c.start_time.asc())
            .apply_labels())

        query, params = asyncpgsa.compile_query(query)

        try:
            rows = await connection.fetch(query, *params)
        except PostgresError:
            raise exceptions.NotFetchedError

        schedule_items = [
            models.schedule_item.t.parse(row, prefix="schedule_items_")
            for row in rows
        ]

        return response.json(response_wrapper.ok(schedule_items))
