"""
Event Bot Server
"""

import asyncio
import datetime
import json
import os

import pendulum


FILENAME = "google_io_2017.json"
EVENT = {
    "name": "Google I/O 2017",
    "description": ("Google I/O is an annual developer festival held at the "
                    "outdoor Shoreline Amphitheatre."),
    "start_date": datetime.date(2017, 5, 17).isoformat(),
    "end_date": datetime.date(2017, 5, 19).isoformat()
}


def get_seeds():
    """Returns seeds for Google I/O 2017 event.

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
    for source in data["speakers"]:
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
        tags_slug_map[source["tag"]] = source["original_id"]
        tags[source["original_id"]] = {
            "name": source["name"],
            "color": source.get("color")
        }

    # Sessions seed
    for source in data["sessions"]:
        sessions[source["id"]] = {
            "title": source["title"],
            "description": source["description"],
            "start_time": pendulum.parse(source["startTimestamp"]).isoformat(),
            "end_time": pendulum.parse(source["endTimestamp"]).isoformat()
        }
        sessions_adds[source["id"]] = {
            "persons": source["speakers"],
            "locations": [source["room"]],
            "tags": [
                tags_slug_map[slug]
                for slug in source["tags"]
                if slug in tags_slug_map
            ]
        }

    return EVENT, persons, locations, tags, sessions, sessions_adds


if __name__ == "__main__":
    print(json.dumps(get_seeds()))
