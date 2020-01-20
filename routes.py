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

        # approximate distance based on duration
        # (500 mph is average speed of jet)
        distance = round(500 * duration, 2)

        for dow in list(DayOfWeek):
            seconds = 0
            while seconds < int(23.5 * 60 * 60):
                route_id += 1
                # Make trip in one direction start a little bit later for
                # realism. Jet stream and all.
                delay = 60 * random.randint(1, 30)
                duration1 = datetime.timedelta(seconds=int(duration * 3600))
                routes.append(Route(
                    id=route_id,
                    start_day=dow,
                    start_time_utc=datetime.time(**get_time_parts(seconds + delay)),
                    duration=duration1,
                    origin_code=port1,
                    destination_code=port2,
                    distance=distance,
                ))

                route_id += 1
                duration2 = datetime.timedelta(seconds=int((duration + random.random()) * 3600))
                routes.append(Route(
                    id=route_id,
                    start_day=dow,
                    start_time_utc=datetime.time(**get_time_parts(seconds)),
                    duration=duration2,
                    origin_code=port2,
                    destination_code=port1,
                    distance=distance,
                ))

                # Wait an extra hour before sending another flight
                seconds += (duration + 1) * 60 * 60

    return routes


def insert_routes(session, airports):
    airport_pairs = build_airport_pairs(airports)
    routes = build_routes(airport_pairs)

    session.add_all(routes)
    session.flush()

    return routes
