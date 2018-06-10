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


class UsersController(HTTPMethodView):

    default_listing = listing.Listing(1, 100, 25)
    """Limits and default options for users listing."""

    @helpers.db_connections.provide_connection()
    async def get(self, request, connection):
        """Returns a list of users."""
        # Validate listing
        try:
            pivot, limit, direction = \
                self.default_listing.validate_from_request(request)
        except ValueError:
            return response.json(
                response_wrapper.error("Listing arguments error"), status=400)

        # Prepare query
        query = select([models.user.t]).select_from(models.user.t)

        # Adjust query according to listing options
        if pivot is not None:
            try:
                query_pivot = query.where(models.user.t.c.id == pivot)
                query_pivot, params = asyncpgsa.compile_query(query_pivot)

                try:
                    row = await connection.fetchrow(query_pivot, *params)
                except PostgresError:
                    raise exceptions.NotFetchedError

                if not row:
                    raise exceptions.NotFoundError

                pivot = models.user.t.parse(row)
            except exceptions.NotFoundError:
                return response.json(
                    response_wrapper.error("Pivot user not found"),
                    status=400)

            if direction == listing.Direction.BEFORE:
                query = (query
                    .where(
                        (models.user.t.c.created_at > pivot["created_at"])
                        | (
                            (models.user.t.c.created_at == pivot["created_at"])
                            & (models.user.t.c.id > pivot["id"])
                        )
                    ))
            elif direction == listing.Direction.AFTER:
                query = (query
                    .where(
                        (models.user.t.c.created_at < pivot["created_at"])
                        | (
                            (models.user.t.c.created_at == pivot["created_at"])
                            & (models.user.t.c.id < pivot["id"])
                        )
                    ))

        # Apply sorting and limit
        if direction == listing.Direction.BEFORE:
            query = (query
                .order_by(models.user.t.c.created_at.asc())
                .order_by(models.user.t.c.id.asc())
                .limit(limit))
        elif direction == listing.Direction.AFTER:
            query = (query
                .order_by(models.user.t.c.created_at.desc())
                .order_by(models.user.t.c.id.desc())
                .limit(limit))

        # Compile query, execute and parse
        query, params = asyncpgsa.compile_query(query)
        try:
            rows = await connection.fetch(query, *params)
        except PostgresError:
            raise exceptions.NotFetchedError

        users = [
            models.user.json_format(models.user.t.parse(row))
            for row in rows
        ]

        if direction == listing.Direction.BEFORE:
            users.reverse()

        # Return the list
        return response.json(response_wrapper.ok(users))

    @helpers.db_connections.provide_connection()
    async def post(self, request, connection):
        """Creates a new user."""

        user = None

        # Create a transaction
        # We need to 1) save user, 2) fetch user from a database
        async with connection.transaction():
            try:
                query = (models.user.t
                    .insert()
                    .returning(models.user.t.c.id))
                query, params = asyncpgsa.compile_query(query)

                id = await connection.fetchval(query, *params)

                query = (select([models.user.t])
                    .select_from(models.user.t)
                    .where(models.user.t.c.id == id))
                query, params = asyncpgsa.compile_query(query)

                try:
                    row = await connection.fetchrow(query, *params)
                except PostgresError:
                    raise exceptions.NotFetchedError

                if not row:
                    raise exceptions.NotFoundError

                user = models.user.json_format(models.user.t.parse(row))
            except (PostgresError, exceptions.DatabaseError):
                raise exceptions.NotCreatedError

        return response.json(response_wrapper.ok(user), status=201)
