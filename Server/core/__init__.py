# traffic_simulation/core/__init__.py
from .simulation import TrafficSimulation
from .utils import generate_random_position

__all__ = ['TrafficSimulation', 'generate_random_position']