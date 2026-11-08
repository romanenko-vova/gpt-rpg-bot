import random


def roll_d20() -> int:
    # На двадцатигранном кубике может выпасть число от 1 до 20.
    return random.randint(1, 20)
