from abc import abstractmethod
from enum import Enum


class Generator:
    @abstractmethod
    def generate(self):
        raise NotImplementedError


class GeneratorType(Enum):
    NAIVE = "naive"
    RANDOM = "random"
    GENETIC = "genetic"
