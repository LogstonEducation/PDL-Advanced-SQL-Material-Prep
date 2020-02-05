import collections
import datetime
import itertools
import random

from models import DayOfWeek
from models import Route
from models import RouteFlight
from models import SeatAssignment
from models import Ticket
from models import SeatType
from models import SeatLocation
from passengers import create_passenger


HUBS_IATA_CODES = frozenset([
    'ATL',
    'BOS',
    'DTW',
    'LAX',
    'MSP',
    'JFK',
    'LGA',
    'SLC',
    'SEA',
])

# Seconds off of departure time for purchase ts
EARLIEST = 6 * 30 * 24 * 60 * 60  # 6 months prior to departure
LATEST = 30 * 60  # 30 minutes prior to departure

# (500 mph is average speed of jet)
MPH = 500
MAX_HOURS = 6
MAX_DISTANCE = MAX_HOURS * MPH


def get_time_parts(seconds):
    seconds = int(seconds)
    second = int(seconds % 60)
    minutes = (seconds - second) // 60
    minute = int(minutes % 60)
    hour = (minutes - minute) // 60

    return {
        'hour': hour,
        'minute': minute,
        'second': second,
    }


def build_airport_pairs(airports):
    codes = set(airport.iata_code for airport in airports)
    non_hub_codes = codes - HUBS_IATA_CODES

    airport_pairs = set(
        frozenset(pair) for pair in itertools.combinations(HUBS_IATA_CODES, 2)
    )

    # All other airports are broken into 8 groups and connect to a single hub
    hubs = list(HUBS_IATA_CODES)
    while non_hub_codes:
        port = random.sample(non_hub_codes, 1)[0]
        non_hub_codes -= {port}

        hub = random.choice(hubs)
        airport_pairs.add(frozenset((hub, port)))

    return airport_pairs


def build_routes(airport_pairs):
    route_id = 0
    routes = []
    while airport_pairs:
        airport_pair = airport_pairs.pop()
        port1, port2 = airport_pair

        duration = random.random() * 2
        # If airports are hubs, lets assume they are far apart
        if airport_pair.issubset(HUBS_IATA_CODES):
            duration += 4

        # Start a bit late into the day. Not all flights
        # start at 00:00.
        delay = random.randint(0, 30) * 60

        duration1 = datetime.timedelta(seconds=int(duration * 60 * 60))

        # Make trip schedule in one direction start a little bit later for
        # realism. Jet stream and all.
        duration2_extention = random.random()
        duration2 = datetime.timedelta(seconds=int((duration + duration2_extention) * 60 * 60))

        # Time at each port
        time_at_port1 = datetime.timedelta(seconds=int(60 * 60))
        time_at_port2 = datetime.timedelta(seconds=int(60 * 60))
        max_round_trip_time = (
            duration1 +
            duration2 +
            time_at_port1 +
            time_at_port2
        ).total_seconds()

        # approximate distance based on duration
        distance = round(MPH * duration, 2)

        for dow in list(DayOfWeek):
            seconds = delay

            # Check if there is enough time for another flight in the day
            while seconds + max_round_trip_time < int(24 * 60 * 60):
                route_id += 1
                routes.append(Route(
                    id=route_id,
                    start_day=dow,
                    start_time_utc=datetime.time(**get_time_parts(seconds)),
                    duration=duration1,
                    origin_code=port1,
                    destination_code=port2,
                    distance=distance,
                ))
                seconds += (duration1 + time_at_port2).total_seconds()

                route_id += 1
                routes.append(Route(
                    id=route_id,
                    start_day=dow,
                    start_time_utc=datetime.time(**get_time_parts(seconds)),
                    duration=duration2,
                    origin_code=port2,
                    destination_code=port1,
                    distance=distance,
                ))
                seconds += (duration2 + time_at_port1).total_seconds()

    return routes


def insert_routes(session, airports):
    airport_pairs = build_airport_pairs(airports)
    routes = build_routes(airport_pairs)

    session.add_all(routes)
    session.flush()

    return routes


def get_ts(week_start, dow, time) -> datetime.datetime:
    return datetime.datetime(
        year=week_start.year,
        month=week_start.month,
        day=week_start.day + dow.value,
        hour=time.hour,
        minute=time.minute,
        second=time.second,
    )


def get_aircraft_by_airport_pair(aircraft, routes):
    aircraft_by_airport_pair = {}

    hub_aircraft = set()
    non_hub_aircraft = set()
    for craft in aircraft:
        # TODO label aircraft as long distance (hub to hub) capable
        if (craft.type.manufacturer == 'Boeing' and craft.type.model == '787-9'):
            hub_aircraft.add(craft)
        else:
            non_hub_aircraft.add(craft)

    aircraft_by_airport_pair = collections.defaultdict(list)
    for route in routes:

        airport_pair = (route.origin_code, route.destination_code)

        if airport_pair not in aircraft_by_airport_pair:
            if frozenset(airport_pair).issubset(HUBS_IATA_CODES):
                aircraft_by_airport_pair[airport_pair].append(hub_aircraft.pop())
            else:
                aircraft_by_airport_pair[airport_pair].append(non_hub_aircraft.pop())

    return aircraft_by_airport_pair


def build_route_flights(session, aircraft, routes, meal_types):
    aircraft_by_airport_pair = get_aircraft_by_airport_pair(aircraft, routes)
    passengers_by_airport_pair = collections.defaultdict(list)

    # for every week for the past 10 years
    week_start = datetime.datetime(2020, 1, 5)

    while week_start < datetime.datetime(2020, 1, 12):
        # for every route in week
        build_route_flight_week(
            session,
            week_start,
            routes,
            aircraft_by_airport_pair,
            passengers_by_airport_pair,
            meal_types,
        )

        week_start += datetime.timedelta(days=7)


def build_route_flight_week(session,
                            week_start,
                            routes,
                            aircraft_by_airport_pair,
                            passengers_by_airport_pair,
                            meal_types):
    route_flights = []

    for route in routes:
        airport_pair = (route.origin_code, route.destination_code)
        aircraft = aircraft_by_airport_pair[airport_pair]
        if len(aircraft) == 0:
            print(f'No craft for {route}', flush=True)
            continue

        index = random.randint(0, len(aircraft) - 1)
        craft = aircraft.pop(index)

        start_ts = get_ts(week_start, route.start_day, route.start_time_utc)
        # Add some randomness to make things interesting
        start_ts += datetime.timedelta(seconds=random.randint(0, 60 * 30))

        end_ts = start_ts + route.duration
        # Add some randomness to make things interesting
        end_ts += datetime.timedelta(seconds=random.randint(-60 * 30, 60 * 30))

        route_flight = RouteFlight(
            route=route,
            start_ts=start_ts,
            end_ts=end_ts,
            aircraft=craft,
        )
        route_flights.append(route_flight)

        # Put the plane back in action for another flight departing from
        # current airport.
        airport_pair = (route.destination_code, route.origin_code)
        aircraft_by_airport_pair[airport_pair].append(craft)

        build_ticket_related_objects(
             session,
             route_flight,
             passengers_by_airport_pair,
             meal_types,
        )


    session.add_all(route_flights)
    session.flush()


def build_ticket_related_objects(session, route_flight, passengers_by_airport_pair, meal_types):
    seat_assignments = []
    tickets = []

    seats = route_flight.aircraft.type.seats

    # Select some percentage of seats
    sold_seats = random.sample(
        population=seats,
        k=random.randint(1, len(seats)),
    )

    for seat in sold_seats:
        passenger = get_passenger(session, route_flight, passengers_by_airport_pair, meal_types)

        seat_assignment = SeatAssignment(
            route_flight=route_flight,
            seat_id=seat.id,
            passenger=passenger,
        )
        seat_assignments.append(seat_assignment)

        purchase_ts_offset = get_purchase_ts_offset(route_flight.start_ts)
        purchase_ts = route_flight.start_ts - datetime.timedelta(seconds=purchase_ts_offset)

        cost = get_cost(route_flight.route.distance, seat, purchase_ts_offset)

        ticket = Ticket(
            seat_assignment=seat_assignment,
            purchase_ts=purchase_ts,
            cost=cost,
        )
        tickets.append(ticket)

        pair = (route_flight.route.origin_code, route_flight.route.destination_code)
        passengers_by_airport_pair[pair].append(passenger)

    session.add_all(seat_assignments)
    session.add_all(tickets)
    session.flush()


def get_passenger(session, route_flight, passengers_by_airport_pair, meal_types):
    # Customers that have flown before might want to fly back
    pair = (route_flight.route.destination_code, route_flight.route.origin_code)
    passengers = passengers_by_airport_pair.get(pair)

    if passengers and random.random() < 0.8:
        index = random.randint(0, len(passengers) - 1)
        passenger = passengers.pop(index)
    else:
        passenger = create_passenger(session, meal_types)

    return passenger


def get_purchase_ts_offset(route_flight_ts):
    # Tuned for 0.75 - 0.8 as most common return value
    frac = random.betavariate(50, 15)

    seconds = (frac - 1) * (EARLIEST - LATEST) + LATEST

    return int(seconds)


def get_cost(distance, aircraft_seat, purchase_ts_offset):
    seat_type_frac = {
        SeatType.first: 3.0,
        SeatType.business: 2.0,
        SeatType.economy: 1.0,
    }.get(aircraft_seat.type)

    seat_location_frac = {
        SeatLocation.window: 0.5,
        SeatLocation.center: 0.0,
        SeatLocation.aisle: 1.0,
    }.get(aircraft_seat.location)

    # Closer to 0 is more savings, closer to 1 is more expensive
    purchase_frac = 1 - ((purchase_ts_offset - LATEST) / (EARLIEST - LATEST))

    base = distance * 0.1
    cost = base * seat_type_frac
    cost = cost + (cost * 0.01) * seat_location_frac
    cost = cost + (cost * purchase_frac)

    return round(cost, 2)


def insert_route_flights(session, aircraft, routes, meal_types):
    build_route_flights(session, aircraft, routes, meal_types)
