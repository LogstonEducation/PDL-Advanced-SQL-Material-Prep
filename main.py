from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aircraft import load_aircraft_types
from models import Base


def main(engine_url):
    engine = create_engine(engine_url, echo=True)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    load_aircraft_types(session)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('engine_url', default='sqlite:///:memory:')

    args = parser.parse_args()

    main(args.engine_url)
