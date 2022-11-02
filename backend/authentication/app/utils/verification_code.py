from random import randint

from ..config import base_config


class RandomGenerator:

    def __init__(self):
        self.upper_bound = base_config.lower_bound
        self.lower_bound = base_config.upper_bound

    def get_verification_code(self):
        code = randint(self.lower_bound, self.upper_bound)
        return str(code)


verification_code = RandomGenerator()
