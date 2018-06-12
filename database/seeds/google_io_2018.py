"""
Event Bot Server
"""

import asyncio
import datetime
import json
import itertools
import os


FILENAME = "google_io_2018.json"
EVENT = {
    "name": "Google I/O 2018",
    "description": ("Google I/O is a developer festival that was held May "
                    "8-10 at the Shoreline Amphitheatre in Mountain View, CA. "
                    "I/O together developers from around the globe annually "
                    "for talks, hands-on learning with Google experts, and a "
                    "first look at Google’s latest developer products."),
    "start_date": datetime.date(2018, 5, 8).isoformat(),
    "end_date": datetime.date(2018, 5, 10).isoformat()
}


def get_seeds():
    """Returns seeds for Google I/O 2018 event.

    Original event's data already contains IDs, that's why we do not
    have to generate our ones.
    """
    persons = {}
    locations = {}
    tags = {}
    sessions = {}
    sessions_adds = {}

    # Load data
    file = open(f"{os.path.dirname(os.path.abspath(__file__))}/{FILENAME}",
                encoding="utf8")
    data = json.loads(file.read())

    # Persons seed
    for source in data["speakers"].values():
        persons[source["id"]] = {
            "name": source["name"]
        }

    # Locations seed
    for source in data["rooms"]:
        locations[source["id"]] = {
            "name": source["name"]
        }

    # Tags seed
    tags_slug_map = {}
    for source in data["tags"]:
        tags_slug_map[source["tag"]] = source["id"]
        tags[source["id"]] = {
            "name": source["name"],
            "color": source.get("color")
        }

    # Sessions seed
    parse_datetime = lambda ts: datetime.datetime.utcfromtimestamp(ts // 1000).replace(microsecond=ts % 1000 * 1000)
    for source in data["sessions"]:
        sessions[source["id"]] = {
            "title": source["title"],
            "description": source["description"],
            "start_time": parse_datetime(source["startTimestamp"]).isoformat(),
            "end_time": parse_datetime(source["endTimestamp"]).isoformat()
        }
        sessions_adds[source["id"]] = {
            "persons": source["speakers"],
            "locations": [source["room"]],
            "tags": [
                tags_slug_map[slug]
                for slug in itertools.chain(source["tagNames"],
                                            source["contentLevels"])
                if slug in tags_slug_map
            ]
        }

    return EVENT, persons, locations, tags, sessions, sessions_adds


if __name__ == "__main__":
    print(json.dumps(get_seeds()))
