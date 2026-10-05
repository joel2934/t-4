from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class Trip:
    pickup: str
    dropoff: str
    distance_km: float
    duration_min: float

    def __post_init__(self):
        if self.distance_km < 0:
            raise ValueError("distance_km must be non-negative")
        if self.duration_min < 0:
            raise ValueError("duration_min must be non-negative")

    def __repr__(self) -> str:
        return (
            f"Trip(pickup={self.pickup!r}, dropoff={self.dropoff!r}, "
            f"distance_km={self.distance_km:.2f}, duration_min={self.duration_min:.1f})"
        )


class Vehicle:
    def __init__(self, make: str, model: str, fuel_level: float = 100.0) -> None:
        self.make = make
        self.model = model
        self.fuel_level = fuel_level

    @property
    def fuel_level(self) -> float:
        return self._fuel_level

    @fuel_level.setter
    def fuel_level(self, value: float) -> None:
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError("fuel_level must be a number") from exc

        if not 0 <= value <= 100:
            raise ValueError("fuel_level must be between 0 and 100")
        self._fuel_level = value

    def __repr__(self) -> str:
        return (
            f"Vehicle(make={self.make!r}, model={self.model!r}, "
            f"fuel_level={self.fuel_level:.1f})"
        )


class FareStrategy(ABC):
    @abstractmethod
    def calculate_fare(self, trip: Trip) -> float:
        ...


class StandardFare(FareStrategy):
    def __init__(self, per_km: float = 1.50, per_min: float = 0.25, base_fare: float = 3.00) -> None:
        self.per_km = per_km
        self.per_min = per_min
        self.base_fare = base_fare

    def calculate_fare(self, trip: Trip) -> float:
        return round(self.base_fare + trip.distance_km * self.per_km + trip.duration_min * self.per_min, 2)


class PremiumFare(FareStrategy):
    def __init__(self, per_km: float = 2.50, per_min: float = 0.60, base_fare: float = 5.00) -> None:
        self.per_km = per_km
        self.per_min = per_min
        self.base_fare = base_fare

    def calculate_fare(self, trip: Trip) -> float:
        return round(self.base_fare + trip.distance_km * self.per_km + trip.duration_min * self.per_min, 2)


class PoolFare(FareStrategy):
    def __init__(self, per_km: float = 0.90, per_min: float = 0.20, base_fare: float = 2.00, discount: float = 0.80) -> None:
        self.per_km = per_km
        self.per_min = per_min
        self.base_fare = base_fare
        self.discount = discount

    def calculate_fare(self, trip: Trip) -> float:
        total = self.base_fare + trip.distance_km * self.per_km + trip.duration_min * self.per_min
        return round(total * self.discount, 2)


class RideBooking:
    def __init__(self, trip: Trip, vehicle: Vehicle, fare_strategy: FareStrategy) -> None:
        self.trip = trip
        self.vehicle = vehicle
        self.fare_strategy = fare_strategy

    def calculate_total(self) -> float:
        return self.fare_strategy.calculate_fare(self.trip)

    def summary(self) -> str:
        return (
            f"Booking summary:\n"
            f"  Trip: {self.trip}\n"
            f"  Vehicle: {self.vehicle}\n"
            f"  Strategy: {self.fare_strategy.__class__.__name__}\n"
            f"  Total fare: ${self.calculate_total():.2f}"
        )

    def with_strategy(self, fare_strategy: FareStrategy) -> "RideBooking":
        return RideBooking(self.trip, self.vehicle, fare_strategy)


class RideHistory:
    def __init__(self, trips: Iterable[Trip] | None = None) -> None:
        self._trips: List[Trip] = list(trips or [])

    def add_trip(self, trip: Trip) -> None:
        if not isinstance(trip, Trip):
            raise TypeError("RideHistory only accepts Trip instances")
        self._trips.append(trip)

    def __len__(self) -> int:
        return len(self._trips)

    def __getitem__(self, index: int) -> Trip:
        return self._trips[index]

    def __iter__(self):
        return iter(self._trips)

    def __repr__(self) -> str:
        trips = ", ".join(repr(trip) for trip in self._trips)
        return f"RideHistory([{trips}])"


def main() -> None:
    trip = Trip(pickup="Downtown", dropoff="Airport", distance_km=18.4, duration_min=28)
    vehicle = Vehicle(make="Toyota", model="Prius", fuel_level=70)
    history = RideHistory([trip])

    standard = RideBooking(trip, vehicle, StandardFare())
    premium = standard.with_strategy(PremiumFare())
    pool = standard.with_strategy(PoolFare())

    print("=== Ride-Sharing Fare Calculator Demo ===")
    print(standard.summary())
    print(premium.summary())
    print(pool.summary())
    print(f"History contains {len(history)} trip(s)")


if __name__ == "__main__":
    main()
