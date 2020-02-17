import random
import string

from models import Passenger
from models import MealType
from models import MealTypeName


def insert_meal_types(session):
    meal_types = [MealType(name=name) for name in MealTypeName]

    session.add_all(meal_types)
    session.flush()

    return meal_types


def clean_name_list(name_list):
    name_list = map(str.title, name_list)

    return list(name_list)


def name_generator_function():
    with open('first_names.txt') as fp:
        first_names = clean_name_list(fp.readlines())

    with open('last_names.txt') as fp:
        last_names = clean_name_list(fp.readlines())

    while True:
        first = random.choice(first_names)
        last = random.choice(last_names)
        yield first.strip(), last.strip()


NAME_GENERATOR = name_generator_function()


def frequent_flyer_number_generator_function():
    chars = string.ascii_uppercase + ''.join(map(str, range(10)))

    # Preload the numbers
    all_numbers = [''.join(random.sample(chars, 10)) for _ in range(1000)]

    while True:
        # Some % of the time, we generate a new number
        if random.random() < 0.25:
            number = ''.join(random.sample(chars, k=10))
            all_numbers.append(number)
            all_numbers = list(set(all_numbers))
        else:
            number = random.choice(all_numbers)

        yield number


FREQUENT_FLYER_NUMBER_GENERATOR = frequent_flyer_number_generator_function()


def create_passenger(session, all_meal_types):
    first_name, last_name = next(NAME_GENERATOR)

    # 10% of people us a frequent flyer number
    frequent_flyer_number = None
    if random.random() < 0.1:
        frequent_flyer_number = next(FREQUENT_FLYER_NUMBER_GENERATOR)

    meal_types = []
    if random.random() < 0.1:
        meal_types = random.sample(
            population=all_meal_types,
            k=random.randint(1, len(all_meal_types)),
        )

    passenger = Passenger(
        first_name=first_name,
        last_name=last_name,
        frequent_flyer_number=frequent_flyer_number,
        preferred_meal_types=meal_types,
    )

    session.add(passenger)

    return passenger
