import random

from models import AircraftType
from models import AircraftSeat
from models import Aircraft
from models import AircraftMaintenanceEvent
from models import MaintenanceEventType
from models import SeatType
from models import SeatLocation


AICRAFT_TYPES = [
    ('Boeing', '737-800', 7.5),
    ('Boeing', '787-9', 11.7),
    ('Airbus', 'A320', 7.6),
]

AIRCRAFT_SEAT_DETAILS = {
    ('Boeing', '737-800'): {
        SeatType.first: {
            'rows': tuple(range(1, 5)),
            'cols': 'ABEF',
            'locs': (
                SeatLocation.window,
                SeatLocation.aisle,
                SeatLocation.aisle,
                SeatLocation.window,
            ),
        },
        SeatType.business: {
            'rows': (7, 8, 10, 11, 12, 14, 15, 20, 21),
            'cols': 'ABCDEF',
            'locs': (
                SeatLocation.window,
                SeatLocation.center,
                SeatLocation.aisle,
                SeatLocation.aisle,
                SeatLocation.center,
                SeatLocation.window,
            ),
        },
        SeatType.economy: {
            'rows': tuple(range(22, 39)),
            'cols': 'ABCDEF',
            'locs': (
                SeatLocation.window,
                SeatLocation.center,
                SeatLocation.aisle,
                SeatLocation.aisle,
                SeatLocation.center,
                SeatLocation.window,
            ),
        },
    },
    ('Boeing', '787-9'): {
        SeatType.first: {
            'rows': tuple(range(1, 5)),
            'cols': 'ABEF',
            'locs': (
                SeatLocation.window,
                SeatLocation.aisle,
                SeatLocation.aisle,
                SeatLocation.window,
            ),
        },
        SeatType.business: {
            'rows': tuple(range(5, 9)),
            'cols': 'ACDEFHK',
            'locs': (
                SeatLocation.window,
                SeatLocation.aisle,
                SeatLocation.aisle,
                SeatLocation.center,
                SeatLocation.aisle,
                SeatLocation.aisle,
                SeatLocation.window,
            ),
        },
        SeatType.economy: {
            'rows': tuple(range(9, 41)),
            'cols': 'ABCDEFHJK',
            'locs': (
                SeatLocation.window,
                SeatLocation.center,
                SeatLocation.aisle,
                SeatLocation.aisle,
                SeatLocation.center,
                SeatLocation.aisle,
                SeatLocation.aisle,
                SeatLocation.center,
                SeatLocation.window,
            ),
        },
    },
    ('Airbus', 'A320'): {
        SeatType.first: {
            'rows': tuple(range(1, 4)),
            'cols': 'ABEF',
            'locs': (
                SeatLocation.window,
                SeatLocation.aisle,
                SeatLocation.aisle,
                SeatLocation.window,
            ),
        },
        SeatType.business: {
            'rows': (7, 8, 10, 11, 12, 20, 21),
            'cols': 'ABCDEF',
            'locs': (
                SeatLocation.window,
                SeatLocation.center,
                SeatLocation.aisle,
                SeatLocation.aisle,
                SeatLocation.center,
                SeatLocation.window,
            ),
        },
        SeatType.economy: {
            'rows': tuple(range(22, 39)),
            'cols': 'ABCDEF',
            'locs': (
                SeatLocation.window,
                SeatLocation.center,
                SeatLocation.aisle,
                SeatLocation.aisle,
                SeatLocation.center,
                SeatLocation.window,
            ),
        },
    },
}


def build_aircraft_seats(session):
    seats_details = []
    for (manufacturer, model), seat_dicts in AIRCRAFT_SEAT_DETAILS.items():
        aircraft_type = session.query(AircraftType).filter(
            AircraftType.manufacturer==manufacturer,
            AircraftType.model==model,
        ).one()

        for seat_type, row_col_dicts in seat_dicts.items():
            cols = row_col_dicts['cols']
            locs = row_col_dicts['locs']
            loc_by_col = {col: loc for col, loc in zip(cols, locs)}

            rows = row_col_dicts['rows']
            seats_details += [
                {
                    'aircraft_type_id': aircraft_type.id,
                    'number': col + str(row),
                    'type': seat_type,
                    'location': loc_by_col.get(col),
                }
                for col in cols
                for row in rows
            ]

    return seats_details


def insert_aircraft_seats(session):
    seats_details = build_aircraft_seats(session)
    seats = [AircraftSeat(**details) for details in seats_details]
    session.add_all(seats)
    session.flush()


def insert_aircraft_types(session):
    types = []
    for type_ in AICRAFT_TYPES:
        types.append(AircraftType(
            manufacturer=type_[0],
            model=type_[1],
            cost_per_seat_mile=type_[2],
        ))

    session.add_all(types)
    session.flush()


def insert_aircraft(session):
    aircraft_types = session.query(AircraftType)
    aircraft_type_count = aircraft_types.count()
    aircraft_types = aircraft_types.all()

    craft = []
    for i in range(900):
        craft.append(Aircraft(
            id=i,
            type_id=aircraft_types[i % aircraft_type_count].id,
            tach_time=random.random() * 100_000,
        ))

    session.add_all(craft)
    session.flush()

    return craft


def insert_aircraft_maintenance_events(session, aircraft):
    events = []
    for craft in aircraft:
        tach_time = int(craft.tach_time)
        max_events = 0
        while tach_time > 1:
            tach_time /= 10
            max_events += 1
        event_count = random.randint(0, max_events)

        for i in range(event_count):
            events.append(AircraftMaintenanceEvent(
                aircraft_id=craft.id,
                event_type=random.choice(list(MaintenanceEventType)),
            ))

    session.add_all(events)
    session.flush()
