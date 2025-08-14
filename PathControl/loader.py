from abc import ABC, abstractmethod


class Loader(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def load(self): ...
    
    @abstractmethod
    def list(self) -> list[str]: ...
