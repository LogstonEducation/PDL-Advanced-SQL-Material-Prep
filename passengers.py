import random

from models import Passenger
from models import MealType
from models import MealTypeName


def insert_meal_types(session):
    meal_types = [MealType(name=name) for name in MealTypeName]

    session.add_all(meal_types)
    session.flush()

    return meal_types


def create_passenger(all_meal_types):
    # TODO create fake name list
    first_name = 'Paul'
    last_name = 'Logston'
    frequent_flyer_number = '123'

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

    return passenger
