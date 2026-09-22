# Flight Block Time

Calculates elapsed flight block times and arrival UTC times from local departure and arrival times across time zone changes.

## Usage

```python
from datetime import datetime, timedelta
from flight_block_time import BlockTimeCalculator, FlightTime, calc_block_time, calc_arrival_time

# Direct calculator instance
calc = BlockTimeCalculator(departure_offset_min=0, arrival_offset_min=60)
dep = datetime(2024, 1, 1, 10, 0)
arr = datetime(2024, 1, 1, 13, 30)
block = calc.block_time(dep, arr)  # timedelta(hours=2, minutes=30)

arrival = calc.arrival_time(dep, timedelta(hours=2, minutes=30))
print(arrival.utc)  # 2024-01-01 12:30:00 (naive UTC)

# Convenience functions
block = calc_block_time(dep, 0, arr, 60)
arrival = calc_arrival_time(dep, 0, timedelta(hours=2, minutes=30))
```

## Why this exists

Flight block time is not simply the difference between two local wall-clock times, because departure and arrival airports may be in different UTC offsets. This library performs the offset adjustment explicitly, storing all results as naive UTC datetimes to avoid ambiguity about timezone-aware arithmetic. The trade-off is that callers must supply offsets as minutes east of UTC, which is an integer and therefore free of the floating point issues that can affect hour-based offsets. The awkward edge is handling overnight flights: the returned block time may be shorter or longer than naive local time subtraction suggests, and arrival times are always expressed in UTC rather than arrival-local time.
