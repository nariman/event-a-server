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


class UserController(HTTPMethodView):

    @helpers.db_connections.provide_connection()
    async def get(self, request, user_id, connection):
        """Returns the user."""

        # Prepare query
        query = (select([models.user.t])
            .select_from(models.user.t)
            .where(models.user.t.c.id == user_id))

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
                response_wrapper.error("User not found"),
                status=404)

        user = models.user.json_format(models.user.t.parse(row))

        # Return the user
        return response.json(response_wrapper.ok(user))


class UserByPlatformController(HTTPMethodView):

    @helpers.db_connections.provide_connection()
    async def get(self, request, user_platform_id, platform_id, connection):
        """Returns the user."""

        # Check, is platform exists
        try:
            query_platform = (select([models.platform.t])
                .select_from(models.platform.t)
                .where(models.platform.t.c.id == platform_id))
            query_platform, params = asyncpgsa.compile_query(query_platform)

            try:
                row = await connection.fetchrow(query_platform, *params)
            except PostgresError:
                raise exceptions.NotFetchedError

            if not row:
                raise exceptions.NotFoundError
        except exceptions.NotFoundError:
            return response.json(
                response_wrapper.error("Platform not found"),
                status=400)

        # Prepare query
        query = (select([models.user_platform.t, models.user.t])
            .select_from(models.user_platform.t.join(
                models.user.t,
                models.user.t.c.id == models.user_platform.t.c.user_id
            ))
            .where(models.user_platform.t.c.platform_id == platform_id)
            .where(models.user_platform.t.c.user_platform_id == user_platform_id)
            .apply_labels())

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
                response_wrapper.error("User not found"),
                status=404)

        user = models.user.json_format(models.user.t.parse(row,
                                                           prefix="users_"))

        # Return the user
        return response.json(response_wrapper.ok(user))


class UserPlatformsController(HTTPMethodView):

    @helpers.db_connections.provide_connection()
    async def get(self, request, user_id, platform_id, connection):
        """Returns the user's platforms."""

        # Check, is user and platform exists
        for name, model, id in [
            ("User", models.user, user_id),
            ("Platform", models.platform, platform_id)
        ]:
            try:
                query = (select([model.t])
                    .select_from(model.t)
                    .where(model.t.c.id == id))
                query, params = asyncpgsa.compile_query(query)

                try:
                    row = await connection.fetchrow(query, *params)
                except PostgresError:
                    raise exceptions.NotFetchedError

                if not row:
                    raise exceptions.NotFoundError
            except exceptions.NotFoundError:
                return response.json(
                    response_wrapper.error(f"{name} not found"),
                    status=404)

        # Prepare query
        query = (select([models.user_platform.t])
            .select_from(models.user_platform.t)
            .where(models.user_platform.t.c.user_id == user_id)
            .where(models.user_platform.t.c.platform_id == platform_id))

        # Compile query, execute and parse
        query, params = asyncpgsa.compile_query(query)
        try:
            rows = await connection.fetch(query, *params)
        except PostgresError:
            raise exceptions.NotFetchedError

        user_platforms = [
            models.user_platform.json_format(models.user_platform.t.parse(row))
            for row in rows
        ]

        # Return the list
        return response.json(response_wrapper.ok(user_platforms))

    @helpers.db_connections.provide_connection()
    async def post(self, request, user_id, platform_id, connection):
        """Creates a new user's platform."""

        # User's platform form
        user_platform = request.json

        # Check, is user and platform exists
        for name, model, id in [
            ("User", models.user, user_id),
            ("Platform", models.platform, platform_id)
        ]:
            try:
                query = (select([model.t])
                    .select_from(model.t)
                    .where(model.t.c.id == id))
                query, params = asyncpgsa.compile_query(query)

                try:
                    row = await connection.fetchrow(query, *params)
                except PostgresError:
                    raise exceptions.NotFetchedError

                if not row:
                    raise exceptions.NotFoundError
            except exceptions.NotFoundError:
                return response.json(
                    response_wrapper.error(f"{name} not found"),
                    status=404)

        # Create a transaction
        # We need to 1) save user, 2) fetch user from a database
        async with connection.transaction():
            try:
                query = (models.user_platform.t
                    .insert()
                    .values(
                        user_id=user_id,
                        platform_id=platform_id,
                        user_platform_id=user_platform["user_platform_id"]
                    )
                )
                query, params = asyncpgsa.compile_query(query)

                id = await connection.fetchval(query, *params)

                query = (select([models.user_platform.t])
                    .select_from(models.user_platform.t)
                    .where(models.user_platform.t.c.user_id == user_id)
                    .where(models.user_platform.t.c.platform_id == platform_id)
                    .where(models.user_platform.t.c.user_platform_id == user_platform["user_platform_id"]))
                query, params = asyncpgsa.compile_query(query)

                try:
                    row = await connection.fetchrow(query, *params)
                except PostgresError:
                    raise exceptions.NotFetchedError

                if not row:
                    raise exceptions.NotFoundError

                user_platform = models.user_platform.json_format(
                    models.user_platform.t.parse(row))
            except (PostgresError, exceptions.DatabaseError):
                raise exceptions.NotCreatedError

        return response.json(response_wrapper.ok(user_platform), status=201)


class UserSavedEventsController(HTTPMethodView):

    default_listing = listing.Listing(1, 100, 25)
    """Limits and default options for events listing."""

    @helpers.db_connections.provide_connection()
    async def get(self, request, user_id, connection):
        """Returns a list of user's saved events."""

        # Validate listing
        try:
            pivot, limit, direction = \
                self.default_listing.validate_from_request(request)
        except ValueError:
            return response.json(
                response_wrapper.error("Listing arguments error"), status=400)

        # Check, is user exists
        try:
            query = (select([models.user.t])
                .select_from(models.user.t)
                .where(models.user.t.c.id == user_id))
            query, params = asyncpgsa.compile_query(query)

            try:
                row = await connection.fetchrow(query, *params)
            except PostgresError:
                raise exceptions.NotFetchedError

            if not row:
                raise exceptions.NotFoundError
        except exceptions.NotFoundError:
            return response.json(
                response_wrapper.error(f"User not found"),
                status=404)

        # Prepare query
        query = (select([models.user_saved_event.t, models.event.t])
            .select_from(models.user_saved_event.t.join(
                models.event.t,
                models.event.t.c.id == models.user_saved_event.t.c.event_id
            ))
            .where(models.user_saved_event.t.c.user_id == user_id)
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
                    .where(
                        (models.event.t.c.start_date > pivot["start_date"])
                        | (
                            (models.event.t.c.start_date == pivot["start_date"])
                            & (models.event.t.c.end_date < pivot["end_date"])
                        ) | (
                            (models.event.t.c.start_date == pivot["start_date"])
                            & (models.event.t.c.end_date == pivot["end_date"])
                            & (models.event.t.c.created_at < pivot["created_at"])
                        ) | (
                            (models.event.t.c.start_date == pivot["start_date"])
                            & (models.event.t.c.end_date == pivot["end_date"])
                            & (models.event.t.c.created_at == pivot["created_at"])
                            & (models.event.t.c.id > pivot["id"])
                        )
                    ))
            elif direction == listing.Direction.AFTER:
                query = (query
                    .where(
                        (models.event.t.c.start_date < pivot["start_date"])
                        | (
                            (models.event.t.c.start_date == pivot["start_date"])
                            & (models.event.t.c.end_date > pivot["end_date"])
                        ) | (
                            (models.event.t.c.start_date == pivot["start_date"])
                            & (models.event.t.c.end_date == pivot["end_date"])
                            & (models.event.t.c.created_at > pivot["created_at"])
                        ) | (
                            (models.event.t.c.start_date == pivot["start_date"])
                            & (models.event.t.c.end_date == pivot["end_date"])
                            & (models.event.t.c.created_at == pivot["created_at"])
                            & (models.event.t.c.id < pivot["id"])
                        )
                    ))

        # Apply sorting and limit
        if direction == listing.Direction.BEFORE:
            query = (query
                .order_by(models.event.t.c.start_date.asc())
                .order_by(models.event.t.c.end_date.desc())
                .order_by(models.event.t.c.created_at.desc())
                .order_by(models.event.t.c.id.asc())
                .limit(limit))
        elif direction == listing.Direction.AFTER:
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

        if direction == listing.Direction.BEFORE:
            events.reverse()

        # Return the list
        return response.json(response_wrapper.ok(events))


class UserSavedEventController(HTTPMethodView):

    @helpers.db_connections.provide_connection()
    async def put(self, request, user_id, event_id, connection):
        """Saves event for the user."""

        # Check, is user and event exists
        for name, model, id in [
            ("User", models.user, user_id),
            ("Event", models.event, event_id)
        ]:
            try:
                query = (select([model.t])
                    .select_from(model.t)
                    .where(model.t.c.id == id))
                query, params = asyncpgsa.compile_query(query)

                try:
                    row = await connection.fetchrow(query, *params)
                except PostgresError:
                    raise exceptions.NotFetchedError

                if not row:
                    raise exceptions.NotFoundError
            except exceptions.NotFoundError:
                return response.json(
                    response_wrapper.error(f"{name} not found"),
                    status=404)

        # If all is ok, save event for user
        query = (models.user_saved_event.t
            .insert()
            .values(user_id=user_id,
                    event_id=event_id))

        # Compile query and execute
        query, params = asyncpgsa.compile_query(query)
        try:
            rows = await connection.execute(query, *params)
        except PostgresError:
            raise exceptions.NotCreatedError

        # Return the HTTP 204
        return response.text("", content_type="application/json", status=204)

    @helpers.db_connections.provide_connection()
    async def delete(self, request, user_id, event_id, connection):
        """Removes event from saved events of the user."""

        query = (models.user_saved_event.t
            .delete()
            .where(models.user_saved_event.t.c.user_id == user_id)
            .where(models.user_saved_event.t.c.event_id == event_id))

        # Compile query and execute
        query, params = asyncpgsa.compile_query(query)
        try:
            rows = await connection.execute(query, *params)
        except PostgresError:
            raise exceptions.NotUpdatedError

        # Return the HTTP 204
        return response.text("", content_type="application/json", status=204)
