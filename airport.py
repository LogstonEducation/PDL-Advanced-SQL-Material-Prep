import csv

from models import Airport


def insert_airports(session):
    with open('iata_codes.csv') as fp:
        reader = list(csv.DictReader(fp))

    airports = []
    for row in reader:
        airports.append(Airport(
            iata_code=row['IATA'],
            name=row['Airport'],
            city=row['City'],
            country=row['Country'],
        ))

    session.add_all(airports)
    session.flush()

    return airports
