from abc import ABC, abstractmethod


class BaseLayer(ABC):
    """Abstract base class for all CA layers."""
    def __init__(self, width: int, height: int):
        self.width, self.height = width, height
        self.grid = [[0]*width for _ in range(height)]

    @abstractmethod
    def update(self, env: 'Environment'):
        pass

