import datetime
import itertools
import random

from models import DayOfWeek
from models import Route
from models import RouteFlight


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
        # (500 mph is average speed of jet)
        distance = round(500 * duration, 2)

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
        day=week_start.day + dow,
        hour=time.hour,
        minute=time.minute,
        second=time.second,
    )


def get_aircraft_by_airport_pair(aircraft, routes):
    aircraft_by_airport_pair = {}

    hub_aircraft = set()
    non_hub_aircraft = set()
    for craft in aircraft:
        if (craft.type.manufacturer == 'Boeing' and craft.type.model == '787-9'):
            hub_aircraft.add(craft)
        else:
            non_hub_aircraft.add(craft)

    aircraft_by_airport_pair = {}
    for route in routes:
        airport_pair = frozenset(route.origin_code, route.destination_code)
        if airport_pair not in aircraft_by_airport_pair:
            if airport_pair.issubset(HUBS_IATA_CODES):
                aircraft_by_airport_pair[airport_pair] = hub_aircraft.pop()
            else:
                aircraft_by_airport_pair[airport_pair] = non_hub_aircraft.pop()

    return aircraft_by_airport_pair


def build_route_flights(aircraft, routes):
    aircraft_by_airport_pair = get_aircraft_by_airport_pair(aircraft, routes)

    route_flights = []
    # for every week for the past 10 years
    week_start = datetime.datetime(2020, 1, 5)
    while week_start < datetime.datetime(2020, 1, 12):
        # for every route in week
        for route in routes:
            airport_pair = frozenset(route.origin_code, route.destination_code)
            craft = aircraft_by_airport_pair[airport_pair]

            start_ts = get_ts(week_start, route.start_day, route.start_time_utc)
            # Add some randomness to make things interesting

            end_ts = start_ts + route.duration
            # Add some randomness to make things interesting

            route_flights.append(RouteFlight(
                route_id=route.id,
                start_ts=start_ts,
                end_ts=end_ts,
                aircraft=craft,
            ))

        week_start += datetime.timedelta(days=7)

    return route_flights


def insert_route_flights(session, aircraft, routes):
    route_flights = build_route_flights(aircraft, routes)

    session.add_all(route_flights)
    session.flush()
