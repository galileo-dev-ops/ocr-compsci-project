from enum import Enum
from typing import Any

class Algorithm(Enum):
    ASTAR = "astar"
    NEURAL = "neural"
    GENETIC = "genetic"
    DIJKSTRA = "dijkstra"
    ANT_COLONY = "ant_colony"
    RRT = "rrt"

class PathfinderFactory:
    @staticmethod
    def create(algorithm: Algorithm, **kwargs) -> Any:
        if algorithm == Algorithm.ASTAR:
            from .astar import AStarPathfinder
            return AStarPathfinder(**kwargs)
        elif algorithm == Algorithm.NEURAL:
            from .neural import NeuralPathfinder
            return NeuralPathfinder(**kwargs)
        elif algorithm == Algorithm.GENETIC:
            from .genetic import GeneticPathfinder
            return GeneticPathfinder(**kwargs)
        elif algorithm == Algorithm.DIJKSTRA:
            from .dijkstra import DijkstraPathfinder
            return DijkstraPathfinder(**kwargs)
        elif algorithm == Algorithm.ANT_COLONY:
            from .antcolony import AntColonyPathfinder
            return AntColonyPathfinder(**kwargs)
        elif algorithm == Algorithm.RRT:
            from .rrt import RRTPathfinder
            return RRTPathfinder(**kwargs)
        raise ValueError(f"Unknown algorithm: {algorithm}")