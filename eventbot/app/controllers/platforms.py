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
from eventbot.lib import listing
from eventbot.lib import response_wrapper


class PlatformsController(HTTPMethodView):

    default_listing = listing.Listing(1, 100, 25)
    """Limits and default options for platforms listing."""

    @helpers.db_connections.provide_connection()
    async def get(self, request, connection):
        """Returns a list of platforms."""
        # Validate listing
        try:
            pivot, limit, direction = \
                self.default_listing.validate_from_request(request)
        except ValueError:
            return response.json(
                response_wrapper.error("Listing arguments error"), status=400)

        # Prepare query
        query = select([models.platform.t]).select_from(models.platform.t)

        # Adjust query according to listing options
        if pivot is not None:
            try:
                query_pivot = query.where(models.platform.t.c.id == pivot)
                query_pivot, params = asyncpgsa.compile_query(query_pivot)

                try:
                    row = await connection.fetchrow(query_pivot, *params)
                except PostgresError:
                    raise exceptions.NotFetchedError

                if not row:
                    raise exceptions.NotFoundError

                pivot = models.platform.t.parse(row)
            except exceptions.NotFoundError:
                return response.json(
                    response_wrapper.error("Pivot platform not found"),
                    status=400)

            if direction == listing.Direction.BEFORE:
                query = (query
                    .where(
                        (models.platform.t.c.slug < pivot["slug"])
                        | (
                            (models.platform.t.c.slug == pivot["slug"])
                            & (models.platform.t.c.id > pivot["id"])
                        )
                    ))
            elif direction == listing.Direction.AFTER:
                query = (query
                    .where(
                        (models.platform.t.c.slug > pivot["slug"])
                        | (
                            (models.platform.t.c.slug == pivot["slug"])
                            & (models.platform.t.c.id < pivot["id"])
                        )
                    ))

        # Apply sorting and limit
        if direction == listing.Direction.BEFORE:
            query = (query
                .order_by(models.platform.t.c.slug.desc())
                .order_by(models.platform.t.c.id.asc())
                .limit(limit))
        elif direction == listing.Direction.AFTER:
            query = (query
                .order_by(models.platform.t.c.slug.asc())
                .order_by(models.platform.t.c.id.desc())
                .limit(limit))

        # Compile query, execute and parse
        query, params = asyncpgsa.compile_query(query)
        try:
            rows = await connection.fetch(query, *params)
        except PostgresError:
            raise exceptions.NotFetchedError

        platforms = [
            models.platform.json_format(models.platform.t.parse(row))
            for row in rows
        ]

        if direction == listing.Direction.BEFORE:
            platforms.reverse()

        # Return the list
        return response.json(response_wrapper.ok(platforms))

    @helpers.db_connections.provide_connection()
    async def post(self, request, connection):
        """Creates a new platform."""

        # Platform form
        platform = request.json

        # Create a transaction
        # We need to 1) save platform, 2) fetch platform from a database
        async with connection.transaction():
            try:
                query = (models.platform.t
                    .insert()
                    .values(slug=platform["slug"],
                            name=platform["name"])
                    .returning(models.platform.t.c.id))
                query, params = asyncpgsa.compile_query(query)

                id = await connection.fetchval(query, *params)

                query = (select([models.platform.t])
                    .select_from(models.platform.t)
                    .where(models.platform.t.c.id == id))
                query, params = asyncpgsa.compile_query(query)

                try:
                    row = await connection.fetchrow(query, *params)
                except PostgresError:
                    raise exceptions.NotFetchedError

                if not row:
                    raise exceptions.NotFoundError

                platform = models.platform.json_format(
                    models.platform.t.parse(row))
            except (PostgresError, exceptions.DatabaseError):
                raise exceptions.NotCreatedError

        return response.json(response_wrapper.ok(platform), status=201)
