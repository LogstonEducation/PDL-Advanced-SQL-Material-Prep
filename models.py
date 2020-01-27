import enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table
from sqlalchemy import (
    ForeignKey,
    Column,
    Integer,
    Float,
    String,
    DateTime,
    Time,
    Enum,
    Interval
)


Base = declarative_base()


class AircraftType(Base):
    __tablename__ = 'aircraft_types'

    id = Column(Integer, primary_key=True)
    manufacturer = Column(String, nullable=False)
    model = Column(String, nullable=False)
    # Cost is in cents
    cost_per_seat_mile = Column(Float)

    seats = relationship(
        'AircraftSeat',
        back_populates='aircraft_type'
    )

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'


class SeatType(enum.Enum):
    first = 'First'
    business = 'Business'
    economy = 'Economy'


class SeatLocation(enum.Enum):
    window = 'Window'
    center = 'Center'
    aisle = 'Aisle'


class AircraftSeat(Base):
    __tablename__ = 'aircraft_seat'

    aircraft_type_id = Column(
        String,
        ForeignKey('aircraft_types.id'),
        primary_key=True
    )
    # Eg. 29C
    number = Column(String, primary_key=True)
    # Eg. 1st class, economy, business
    type = Column(Enum(SeatType), nullable=False)
    # location (Asile, Window, Center, etc, 10 seats across)
    location = Column(Enum(SeatLocation), nullable=False)

    aircraft_type = relationship(
        'AircraftType',
        uselist=False,
        back_populates='seats'
    )

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.aircraft_type_id} / {self.number}>'


class Aircraft(Base):
    __tablename__ = 'aircraft'

    # Eg. Tail ID
    id = Column(Integer, primary_key=True)
    type_id = Column(
        Integer,
        ForeignKey('aircraft_types.id'),
        primary_key=True
    )
    tach_time = Column(Float)

    type = relationship('AircraftType')

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'


class MaintenanceEventType(enum.Enum):
    oil = 'Oil'
    turbine = 'Turbine'
    tires = 'Tires'


class AircraftMaintenanceEvent(Base):
    __tablename__ = 'aircraft_maintenance_events'

    id = Column(Integer, primary_key=True)
    aircraft_id = Column(Integer, ForeignKey('aircraft.id'), nullable=False)
    event_type = Column(Enum(MaintenanceEventType, nullable=False))

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'


class Airport(Base):
    __tablename__ = 'airports'

    iata_code = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.iata_code}>'


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
    start_day = Column(Enum(DayOfWeek), nullable=False)
    # Time of day route starts from start location (in UTC)
    start_time_utc = Column(Time, nullable=False)
    duration = Column(Interval, nullable=False)
    origin_code = Column(String, ForeignKey('airports.iata_code'), nullable=False)
    destination_code = Column(String, ForeignKey('airports.iata_code'), nullable=False)
    distance = Column(Float, nullable=False)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'


class RouteFlight(Base):
    """
    An instance of a Route.
    """
    __tablename__ = 'route_flights'

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey('routes.id'), nullable=False)
    start_ts = Column(DateTime, nullable=False)
    end_ts = Column(DateTime, nullable=False)
    aircraft_id = Column(Integer, ForeignKey('aircraft.id'), nullable=False)

    route = relationship('Route')
    aircraft = relationship('Aircraft')

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'


passenger_preferred_meal_types = Table(
    'passenger_preferred_meal_types', Base.metadata,
    Column('passenger_id', Integer, ForeignKey('passengers.id')),
    Column('meal_type_id', Integer, ForeignKey('meal_types.id'))
)


class Passenger(Base):
    __tablename__ = 'passengers'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    frequent_flyer_number = Column(String)

    preferred_meal_types = relationship(
        'MealType',
        secondary=passenger_preferred_meal_types,
    )

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'


class SeatAssignment(Base):
    __tablename__ = 'seat_assignments'

    id = Column(Integer, primary_key=True)
    route_flight_id = Column(Integer, ForeignKey('route_flights.id'), nullable=False)
    seat_id = Column(String, ForeignKey('aircraft_seat.number'), nullable=False)
    passenger_id = Column(String, ForeignKey('passengers.id'), nullable=False)

    route_flight = relationship('RouteFlight')
    passenger = relationship('Passenger')
    ticket = relationship(
        "Ticket",
        uselist=False,
        back_populates="seat_assignment",
    )

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'


class Ticket(Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True)
    seat_assignment_id = Column(
        Integer,
        ForeignKey('seat_assignments.id'),
        nullable=False,
    )
    purchase_ts = Column(DateTime, nullable=False)
    cost = Column(Float, nullable=False)

    seat_assignment = relationship(
        "SeatAssignment",
        back_populates="ticket",
    )

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id} / {self.seat_assignment_id}>'


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

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'
