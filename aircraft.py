from models import AircraftType
from models import AircraftSeatMap
from models import Aircraft
from models import AircraftMaintenanceEvent
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


def build_seat_map(session):
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


def insert_seat_maps(session):
    seats_details = build_seat_map(session)
    seats = [AircraftSeatMap(**details) for details in seats_details]
    session.add_all(seats)
    session.flush()


def insert_aircraft_types(session):
    for type_ in AICRAFT_TYPES:
        session.add(AircraftType(
            manufacturer=type_[0],
            model=type_[1],
            cost_per_seat_mile=type_[2],
        ))

    session.flush()


def insert_aircraft(session):



Aircraft
    # 249
    id = Column(Integer, primary_key=True)
    type = Column(String, ForeignKey('aircraft_types.id'))
    tach_time = Column(Float)

AircraftMaintenanceEvent
    aircraft_id = Column(Integer, ForeignKey('aircraft.id'), primary_key=True)
    event_type = Column(Enum(MaintenanceEventType))
    service_start_ts = Column(DateTime, primary_key=True)
    service_end_ts = Column(DateTime)
    location = Column(String, ForeignKey('airports.iata_code'))

