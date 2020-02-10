import random

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aircraft import insert_aircraft_seats
from aircraft import insert_aircraft_types
from aircraft import insert_aircraft
from aircraft import insert_aircraft_maintenance_events
from airports import insert_airports
from passengers import insert_meal_types
from routes import insert_routes
from routes import insert_route_flights
from copyright import insert_copyright
from models import Base


def main(engine_url, weeks, verbose=False):
    random.seed(2020)

    engine = create_engine(engine_url, echo=verbose)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    insert_copyright(session)
    meal_types = insert_meal_types(session)
    insert_aircraft_types(session)
    insert_aircraft_seats(session)
    aircraft = insert_aircraft(session)
    insert_aircraft_maintenance_events(session, aircraft)
    airports = insert_airports(session)
    routes = insert_routes(session, airports)
    insert_route_flights(session, weeks, aircraft, routes, meal_types)

    session.commit()
    session.close()

    engine.dispose()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('engine_url', help='eg. "sqlite:///:memory:"')
    parser.add_argument('--verbose', '-v', action='count', default=0)
    parser.add_argument('--weeks', '-w', type=int, default=1)

    args = parser.parse_args()

    main(args.engine_url, args.weeks, bool(args.verbose))
