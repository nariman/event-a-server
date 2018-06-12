"""
Event Bot Server
"""

import asyncio
import functools
import itertools
import time

import aiohttp

import seeds.google_io_2016
import seeds.google_io_2017
import seeds.google_io_2018


SERVER_URL = "https://e.nariman.io"


# Each module (seed) should have an `get_seeds` method, that returns a
# tuple in the next format:
#   (event, persons, locations, tags, sessions)
#
# Where:
#   - `event` is a `dict` w/ Event attributes (according to API)
#   - `persons` is a `dict`, where keys are unique IDs, which are
#     needed only for seeder purposes, and values is a `dict` w/ Person
#     attributes (according to API)
#   - `locations` is a `dict`, where keys are unique IDs, which are
#     needed only for seeder purposes, and values is a `dict` w/
#     Location attributes (according to API)
#   - `tags` is a `dict`, where keys are unique IDs, which are
#     needed only for seeder purposes, and values is a `dict` w/ Tag
#     attributes (according to API)
#   - `sessions` is a `dict`, where keys are unique IDs, which are
#     needed only for seeder purposes, and values is a `dict` w/
#     Session attributes (according to API)
#   - `sessions_adds` is a `dict`, where keys are IDs of corresponding
#     sessions, and values is a `dict` with `event`, `locations` and
#     `tags` attributes, each one containing `list` with corresponding
#     IDs of returned data in a tuple.
#
# In other words, IDs are needed for the ability to specify
# corresponding objects in a Session object. You can use an `uuid`
# standard Python library to achieve this, if the source doesn't
# contains own IDs.

seeds_list = [
    seeds.google_io_2016,
    seeds.google_io_2017,
    seeds.google_io_2018
]


async def main(semaphore):
    requests_number = 0
    requests_time = 0

    async def request(semaphore, coro_or_future, callback=None):
        async with semaphore:
            conn = await coro_or_future
            resp = await conn.json()
            conn.close()

            return resp["data"] if resp is not None else None, callback

    async with aiohttp.ClientSession() as session:
        for seeds_module in seeds_list:
            print(f"Processing {seeds_module}...")
            event, persons, locations, tags, sessions, sessions_adds = seeds_module.get_seeds()
            print("Fetched data...")

            # There's is no need in timing this request
            async with session.post(f"{SERVER_URL}/events", json=event) as response:
                event = (await response.json())["data"]

            print("Event created...")

            _1 = event["id"]
            futures = []

            for name, source in (("persons", persons),
                                 ("locations", locations),
                                 ("tags", tags),
                                 ("sessions", sessions)):
                # Push an object to the server and replace it in the
                # original dict with a created object (by the same ID)
                for key in source:
                    futures.append(request(
                        semaphore,
                        session.post(f"{SERVER_URL}/events/{_1}/{name}", json=source[key]),
                        functools.partial(
                            lambda key, source, response: source.update({key: response}),
                            key,
                            source
                        )
                    ))

            requests_number += len(futures)
            start_time = time.time()
            results = await asyncio.gather(*futures)
            end_time = time.time()
            requests_time += end_time - start_time

            print(f"Persons, locations, tags and sessions created in {end_time - start_time} seconds, {len(futures) / (end_time - start_time)} req/s.")

            for response, callback in results:
                callback(response)

            futures = []

            for key in sessions_adds:
                _2 = sessions[key]["id"]

                for name, updated, source in (("persons", persons, sessions_adds[key]["persons"]),
                                              ("locations", locations, sessions_adds[key]["locations"]),
                                              ("tags", tags, sessions_adds[key]["tags"])):
                    for id in source:
                        _3 = updated[id]["id"]
                        futures.append(request(
                            semaphore,
                            session.put(f"{SERVER_URL}/events/{_1}/sessions/{_2}/{name}/{_3}")
                        ))

            requests_number += len(futures)
            start_time = time.time()
            await asyncio.gather(*futures)
            end_time = time.time()
            requests_time += end_time - start_time

            print(f"Sessions additionals pushed in {end_time - start_time} seconds, {len(futures) / (end_time - start_time)} req/s.")

    print(f"Done in {end_time - start_time} seconds.")
    print(f"{requests_number / requests_time} req/s.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    semaphore = asyncio.Semaphore(1000)
    loop.run_until_complete(main(semaphore))
