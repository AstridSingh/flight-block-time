"""Tests for flight_block_time.core."""

import unittest
from datetime import datetime, timedelta, timezone

from flight_block_time import BlockTimeCalculator, FlightTime, calc_arrival_time, calc_block_time


class TestBlockTimeCalculator(unittest.TestCase):
    def test_same_timezone_positive_duration(self):
        calc = BlockTimeCalculator(0, 0)
        dep = datetime(2024, 1, 1, 10, 0)
        arr = datetime(2024, 1, 1, 12, 30)
        self.assertEqual(calc.block_time(dep, arr), timedelta(hours=2, minutes=30))

    def test_crossing_timezone_change(self):
        calc = BlockTimeCalculator(0, 60)
        dep = datetime(2024, 1, 1, 10, 0)
        arr = datetime(2024, 1, 1, 13, 30)
        self.assertEqual(calc.block_time(dep, arr), timedelta(hours=2, minutes=30))

    def test_westward_departure_negative_offset(self):
        calc = BlockTimeCalculator(-300, -360)
        dep = datetime(2024, 1, 1, 8, 0)
        arr = datetime(2024, 1, 1, 10, 0)
        self.assertEqual(calc.block_time(dep, arr), timedelta(hours=3))

    def test_overnight_flight(self):
        calc = BlockTimeCalculator(120, 0)
        dep = datetime(2024, 1, 1, 22, 0)
        arr = datetime(2024, 1, 2, 6, 30)
        self.assertEqual(calc.block_time(dep, arr), timedelta(hours=10, minutes=30))

    def test_arrival_time_basic(self):
        calc = BlockTimeCalculator(0, 0)
        dep = datetime(2024, 1, 1, 9, 0)
        block = timedelta(hours=1, minutes=45)
        result = calc.arrival_time(dep, block)
        self.assertIsInstance(result, FlightTime)
        self.assertEqual(result.utc, datetime(2024, 1, 1, 10, 45))

    def test_arrival_time_crossing_timezone(self):
        calc = BlockTimeCalculator(60, 0)
        dep = datetime(2024, 1, 1, 9, 0)
        block = timedelta(hours=2)
        result = calc.arrival_time(dep, block)
        self.assertEqual(result.utc, datetime(2024, 1, 1, 10, 0))

    def test_arrival_time_rejects_negative_block(self):
        calc = BlockTimeCalculator(0, 0)
        dep = datetime(2024, 1, 1, 9, 0)
        with self.assertRaises(ValueError):
            calc.arrival_time(dep, timedelta(minutes=-5))


class TestConvenienceFunctions(unittest.TestCase):
    def test_calc_block_time(self):
        dep = datetime(2024, 1, 1, 12, 0)
        arr = datetime(2024, 1, 1, 14, 0)
        self.assertEqual(calc_block_time(dep, 0, arr, 0), timedelta(hours=2))

    def test_calc_arrival_time(self):
        dep = datetime(2024, 1, 1, 12, 0)
        block = timedelta(hours=3)
        result = calc_arrival_time(dep, 0, block)
        self.assertIsInstance(result, FlightTime)
        self.assertEqual(result.utc, datetime(2024, 1, 1, 15, 0))


class TestFlightTime(unittest.TestCase):
    def test_requires_naive_datetime(self):
        with self.assertRaises(ValueError):
            FlightTime(utc=datetime(2024, 1, 1, tzinfo=timezone.utc))
