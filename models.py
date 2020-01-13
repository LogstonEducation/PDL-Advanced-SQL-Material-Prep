import enum
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    ForeignKey,
    Column,
    Integer,
    Float,
    String,
    DateTime,
    Time,
    Enum,
    Text,
    Interval
)


Base = declarative_base()


class AircraftType(Base):
    __tablename__ = 'aircraft_types'

    id = Column(Integer, primary_key=True)
    manufacturer = Column(String)
    model = Column(String)
    # Cost is in cents
    cost_per_seat_mile = Column(Float)

    seat_map = relationship(
        'AircraftSeatMap',
        uselist=False,
        back_populates='aircraft_type'
    )


class SeatType(enum.Enum):
    first = 'First'
    business = 'Business'
    economy = 'Economy'


class SeatLocation(enum.Enum):
    window = 'Window'
    center = 'Center'
    aisle = 'Aisle'


class AircraftSeatMap(Base):
    __tablename__ = 'aircraft_seat_map'

    model = Column(String, ForeignKey('aircraft_types.id'), primary_key=True)
    # Eg. 29C
    number = Column(String, primary_key=True)
    # Eg. 1st class, economy, business
    type = Column(Enum(SeatType))
    # location (Asile, Window, Center, etc, 10 seats across)
    location = Column(Enum(SeatLocation))

    aircraft_type = relationship('AircraftType', back_populates='seat_map')


class Aircraft(Base):
    __tablename__ = 'aircraft'

    # Eg. Tail ID
    id = Column(Integer, primary_key=True)
    type = Column(String, ForeignKey('aircraft_types.id'))
    tach_time = Column(Float)


class MaintenanceEventType(enum.Enum):
    oil = 'Oil'
    turbine = 'Turbine'
    tires = 'Tires'


class AircraftMaintenanceEvent(Base):
    __tablename__ = 'aircraft_maintenance_events'
    # Aircraft ID (tail ID), Maintenance event, start date, end date, location

    aircraft_id = Column(Integer, ForeignKey('aircraft.id'), primary_key=True)
    event_type = Column(Enum(MaintenanceEventType))
    service_start_ts = Column(DateTime, primary_key=True)
    service_end_ts = Column(DateTime)
    location = Column(String, ForeignKey('airports.iata_code'))


class Airport(Base):
    __tablename__ = 'airports'

    iata_code = Column(String, primary_key=True)
    service_start_ts = Column(DateTime)
    service_end_ts = Column(DateTime)


class DayOfWeek(enum.Enum):
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6


class Route(Base):
    __tablename__ = 'routes'

    # Eg. 3728 in DL3728
    id = Column(Integer, primary_key=True)
    # Day of week route starts from start location
    start_day = Column(Enum(DayOfWeek))
    # Time of day route starts from start location (in UTC)
    start_time_utc = Column(Time)
    duration = Column(Interval)
    origin_code = Column(String, ForeignKey('airports.iata_code'))
    destination_code = Column(String, ForeignKey('airports.iata_code'))
    distance = Column(Float)


class RouteFlight(Base):
    """
    An instance of a Route.
    """
    __tablename__ = 'route_flights'

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey('routes.id'))
    start_ts = Column(DateTime)
    end_ts = Column(DateTime)
    aircraft_id = Column(Integer, ForeignKey('aircraft.id'))


passenger_preferred_meal_types = Table(
    'passenger_preferred_meal_types', Base.metadata,
    Column('passenger_id', Integer, ForeignKey('passengers.id')),
    Column('meal_type_id', Integer, ForeignKey('meal_types.id'))
)


class Passenger(Base):
    __tablename__ = 'passengers'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    frequent_flyer_number = Column(String)

    preferred_meal_types = relationship(
        'MealType',
        secondary=passenger_preferred_meal_types,
    )


class SeatAssignment(Base):
    __tablename__ = 'seat_assignments'

    id = Column(Integer, primary_key=True)
    route_flight_id = Column(Integer, ForeignKey('route_flights.id'))
    seat_map_id = Column(String, ForeignKey('aircraft_seat_map.number'))
    passenger_id = Column(String, ForeignKey('passengers.id'))

    ticket = relationship(
        'Ticket',
        uselist=False,
        back_populates='seat_assignment'
    )


class Ticket(Base):
    __tablename__ = 'tickets'

    seat_assignment_id = Column(
        Integer,
        ForeignKey('seat_assignments.id'),
        primary_key=True
    )
    purchase_ts = Column(DateTime)
    cost = Column(Float)

    seat_assignment = relationship(
        'SeatAssignment',
        back_populates='ticket'
    )


class MealTypeName(enum.Enum):
    vegan = 'Vegan'
    vegetarian = 'Vegetarian'
    kosher = 'Kosher'
    halal = 'Halal'
    low_salt = 'Low Salt'
    diabetic = 'Diabetic'


class MealType(Base):
    __tablename__ = 'meal_types'

    id = Column(Integer, primary_key=True)
    name = Column(Enum(MealTypeName))


class FrequentFlyer(Base):
    __tablename__ = 'frequent_flyer'

    passenger_id = Column(String, ForeignKey('passengers.id'), primary_key=True)
    route_flight_id = Column(Integer, ForeignKey('route_flights.id'), primary_key=True)
