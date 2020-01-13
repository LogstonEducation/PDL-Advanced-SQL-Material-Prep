from models import AircraftType


TYPES = [
    ('Boeing', '737-800', 7.5),
    ('Boeing', '787-9', 11.7),
    ('Airbus', 'A320', 7.6),
]


def load_aircraft_types(session):
    for type_ in TYPES:
        session.add(AircraftType(
            manufacturer=type_[0],
            model=type_[1],
            cost_per_seat_mile=type_[2],
        ))

    session.flush()
