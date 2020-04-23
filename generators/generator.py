from abc import abstractmethod


class Generator:
    @abstractmethod
    def generate(self):
        raise NotImplementedError
