"""Core implementation for flight block time calculations.

A flight's block time is the elapsed time between departure and arrival,
independent of local clock settings. This module computes block time and
arrival time when departure, scheduled duration, and time zone offsets are
known.

The design uses integer minutes internally. This avoids floating point drift
when adding durations, and keeps the implementation deterministic across
platforms. Offsets are represented as minutes east of UTC (positive east),
matching ISO 8601 convention.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class FlightTime:
    """A point in a flight, expressed in UTC.

    Attributes:
        utc: The UTC wall time as a naive datetime. Storing naive UTC avoids
            confusion from mixing aware and naive datetimes.
    """

    utc: datetime

    def __post_init__(self) -> None:
        if self.utc.tzinfo is not None:
            raise ValueError("utc must be naive")


class BlockTimeCalculator:
    """Calculates block times using a fixed set of time zone offsets.

    Offsets are measured in minutes east of UTC. The calculator is immutable
    and safe to share across threads.
    """

    def __init__(self, departure_offset_min: int, arrival_offset_min: int) -> None:
        """Create a calculator for a given city pair.

        Args:
            departure_offset_min: Offset at departure airport, minutes east of UTC.
            arrival_offset_min: Offset at arrival airport, minutes east of UTC.
        """
        self.departure_offset = departure_offset_min
        self.arrival_offset = arrival_offset_min

    def block_time(
        self,
        departure_local: datetime,
        arrival_local: datetime,
    ) -> timedelta:
        """Return elapsed block time between two local wall-clock times.

        Both arguments are naive datetimes in their respective airport local
        times. The subtraction is performed in UTC after applying the offsets.
        """
        dep_utc = departure_local - timedelta(minutes=self.departure_offset)
        arr_utc = arrival_local - timedelta(minutes=self.arrival_offset)
        return arr_utc - dep_utc

    def arrival_time(self, departure_local: datetime, block_time: timedelta) -> FlightTime:
        """Compute arrival UTC time from a departure and block duration.

        Args:
            departure_local: Naive local time at departure airport.
            block_time: Non-negative elapsed time.

        Returns:
            FlightTime whose utc field is a naive datetime in UTC.
        """
        if block_time < timedelta(0):
            raise ValueError("block_time must be non-negative")
        dep_utc = departure_local - timedelta(minutes=self.departure_offset)
        arr_utc = dep_utc + block_time
        return FlightTime(utc=arr_utc)


def calc_block_time(
    departure_local: datetime,
    departure_offset_min: int,
    arrival_local: datetime,
    arrival_offset_min: int,
) -> timedelta:
    """Compute block time from two local times and their UTC offsets.

    Convenience wrapper around BlockTimeCalculator.
    """
    return BlockTimeCalculator(departure_offset_min, arrival_offset_min).block_time(
        departure_local, arrival_local
    )


def calc_arrival_time(
    departure_local: datetime,
    departure_offset_min: int,
    block_time: timedelta,
) -> FlightTime:
    """Compute arrival UTC time from a departure and block time.

    Convenience wrapper around BlockTimeCalculator.
    """
    return BlockTimeCalculator(departure_offset_min, 0).arrival_time(
        departure_local, block_time
    )
