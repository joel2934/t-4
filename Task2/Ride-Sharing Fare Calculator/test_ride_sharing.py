import unittest

from ride_sharing import (
    FareStrategy,
    PoolFare,
    PremiumFare,
    RideBooking,
    RideHistory,
    StandardFare,
    Trip,
    Vehicle,
)


class RideSharingTest(unittest.TestCase):
    def test_trip_repr(self):
        trip = Trip("A", "B", distance_km=10.0, duration_min=15.0)
        self.assertIn("pickup='A'", repr(trip))
        self.assertIn("distance_km=10.00", repr(trip))

    def test_trip_validation(self):
        with self.assertRaises(ValueError):
            Trip("A", "B", distance_km=-1.0, duration_min=10.0)
        with self.assertRaises(ValueError):
            Trip("A", "B", distance_km=10.0, duration_min=-5.0)

    def test_vehicle_fuel_level_validation(self):
        with self.assertRaises(ValueError):
            Vehicle("Honda", "Civic", fuel_level=150)
        with self.assertRaises(TypeError):
            Vehicle("Honda", "Civic", fuel_level="full")

        vehicle = Vehicle("Honda", "Civic", fuel_level=50)
        self.assertEqual(vehicle.fuel_level, 50)
        vehicle.fuel_level = 75
        self.assertEqual(vehicle.fuel_level, 75)

    def test_standard_fare_calculation(self):
        trip = Trip("Start", "End", distance_km=12.0, duration_min=20.0)
        fare = StandardFare().calculate_fare(trip)
        self.assertEqual(fare, 3.00 + 12.0 * 1.50 + 20.0 * 0.25)

    def test_premium_fare_calculation(self):
        trip = Trip("Start", "End", distance_km=5.0, duration_min=10.0)
        fare = PremiumFare().calculate_fare(trip)
        self.assertEqual(fare, 5.00 + 5.0 * 2.50 + 10.0 * 0.60)

    def test_pool_fare_calculation(self):
        trip = Trip("Start", "End", distance_km=8.0, duration_min=15.0)
        fare = PoolFare().calculate_fare(trip)
        expected = round((2.00 + 8.0 * 0.90 + 15.0 * 0.20) * 0.80, 2)
        self.assertEqual(fare, expected)

    def test_ride_booking_strategy_switch(self):
        trip = Trip("A", "B", distance_km=7.5, duration_min=12.0)
        vehicle = Vehicle("Ford", "Focus", fuel_level=85)
        standard_booking = RideBooking(trip, vehicle, StandardFare())
        premium_booking = standard_booking.with_strategy(PremiumFare())

        self.assertNotEqual(standard_booking.calculate_total(), premium_booking.calculate_total())
        self.assertIn("PremiumFare", premium_booking.summary())

    def test_ride_history_len_and_getitem(self):
        trip1 = Trip("Pickup", "Dropoff", distance_km=2.0, duration_min=5.0)
        trip2 = Trip("Pickup2", "Dropoff2", distance_km=3.5, duration_min=8.0)
        history = RideHistory([trip1])
        history.add_trip(trip2)

        self.assertEqual(len(history), 2)
        self.assertIs(history[0], trip1)
        self.assertIs(history[1], trip2)

    def test_ride_history_rejects_non_trip(self):
        history = RideHistory()
        with self.assertRaises(TypeError):
            history.add_trip(object())


if __name__ == "__main__":
    unittest.main()
