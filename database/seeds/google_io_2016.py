"""
Event Bot Server
"""

import asyncio
import datetime
import json
import os
import uuid

import pendulum


FILENAME = "google_io_2016.json"
EVENT = {
    "name": "Google I/O 2016",
    "description": ("Google I/O is an annual developer festival."),
    "start_date": datetime.date(2016, 5, 18).isoformat(),
    "end_date": datetime.date(2016, 5, 20).isoformat()
}


def get_seeds():
    """Returns seeds for Google I/O 2018 event.

    Original event's data already contains some IDs, that's why we do
    not have to generate our ones.
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
    locations_set = set()
    locations_name_map = {}
    for source in data["sessions"]:
        locations_set.add(source["room"])
    for location in locations_set:
        id = str(uuid.uuid4())
        locations_name_map[location] = id
        locations[id] = {
            "name": location
        }

    # Tags seed
    tags_slug_map = {}
    for source in data["tags"].values():
        id = str(uuid.uuid4())
        tags_slug_map[source["tag"]] = id
        tags[id] = {
            "name": source["name"],
            "color": None
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
            "persons": source["speakers"] or [],  # source can be null
            "locations": [locations_name_map[source["room"]]],
            "tags": [
                tags_slug_map[slug]
                for slug in source["tags"]
                if slug in tags_slug_map
            ]
        }

    return EVENT, persons, locations, tags, sessions, sessions_adds


if __name__ == "__main__":
    print(json.dumps(get_seeds()))
