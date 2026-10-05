# Ride-Sharing Fare Calculator

A small Python project implementing a ride-sharing fare calculator with:

- `Trip` dataclass for trip details
- `Vehicle` class with validated `fuel_level`
- `FareStrategy` abstract base class and concrete strategies:
  - `StandardFare`
  - `PremiumFare`
  - `PoolFare`
- `RideBooking` composition to calculate fares using interchangeable pricing strategies
- `RideHistory` collection with `__len__` and `__getitem__`

## Running

```bash
python ride_sharing.py
```

## Testing

```bash
python -m unittest test_ride_sharing.py
```
