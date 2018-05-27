"""
Event Bot Server
"""

import logging
import time
import typing


TIMESTAMP_BITS = 41
TIMESTAMP_BITS = 10
SEQUENCE_NUMBER_BITS = 12
EPOCH = 1514764800  # 1st second of 2018


logger = logging.getLogger(__name__)

max_machine_id = -1 ^ (-1 << TIMESTAMP_BITS)

timestamp_shift = TIMESTAMP_BITS + SEQUENCE_NUMBER_BITS
machine_id_shift = SEQUENCE_NUMBER_BITS

machine_id_mask = -1 ^ (-1 << TIMESTAMP_BITS) << machine_id_shift
sequence_number_mask = -1 ^ (-1 << SEQUENCE_NUMBER_BITS)


def timestamp_of_snowflake(snowflake: int) -> int:
    """Get timestamp in ms from config epoch from Snowflake ID."""
    return snowflake >> timestamp_shift


def real_timestamp_of_snowflake(snowflake: int) -> int:
    """Get timestamp in ms from computer epoch - 01.01.1970."""
    return timestamp_of_snowflake(snowflake) + EPOCH


def machine_id_of_snowflake(snowflake: int) -> int:
    """Get Machine ID from Snowflake ID."""
    return (snowflake & machine_id_mask) >> machine_id_shift


def sequence_number_of_snowflake(snowflake: int) -> int:
    """Get Sequence Number from Snowflake ID."""
    return snowflake & sequence_number_mask


def first_snowflake_for_timestamp(timestamp: int, machine_id: int=0) -> int:
    """First Snowflake ID for timestamp and Machine ID."""
    return (
        ((timestamp - EPOCH) << timestamp_shift) |
        (machine_id << machine_id_shift) |
        0
    )


def generator(machine_id: int,
              sleep=lambda x: time.sleep(x / 1000.0),
              now=lambda: int(time.time() * 1000)):
    assert 0 <= machine_id <= max_machine_id

    last_timestamp = -1
    sequence_number = 0

    while True:
        timestamp = now()

        if last_timestamp > timestamp:
            logger.warning(
                "Clock is moving backwards. Waiting until %i" % last_timestamp)
            sleep(last_timestamp - timestamp)
            continue

        if last_timestamp == timestamp:
            sequence_number = (sequence_number + 1) & sequence_number_mask
            if sequence_number == 0:
                logger.warning("Sequence overflow")
                sequence_number = -1 & sequence_number_mask
                sleep(1)
                continue
        else:
            sequence_number = 0

        last_timestamp = timestamp

        yield (
            ((timestamp - EPOCH) << timestamp_shift) |
            (machine_id << machine_id_shift) |
            sequence_number
        )
