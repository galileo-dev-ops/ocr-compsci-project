from typing import List, Tuple
import numpy as np
import random

class AntColonyPathfinder:
    def __init__(self, rows: int = 6, cols: int = 6, 
                 n_ants: int = 20, n_iterations: int = 50,
                 decay: float = 0.1, alpha: float = 1, beta: float = 2):
        self.rows = rows
        self.cols = cols
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta
        
    def find_path(self, start: int, end: int) -> List[int]:
        start_pos = ((start - 1) // self.cols, (start - 1) % self.cols)
        end_pos = ((end - 1) // self.cols, (end - 1) % self.cols)
        
        # Initialize pheromone matrix
        pheromone = np.ones((self.rows * self.cols, self.rows * self.cols)) * 0.1
        best_path = None
        best_length = float('inf')
        
        for _ in range(self.n_iterations):
            paths = self._simulate_ants(start_pos, end_pos, pheromone)
            
            # Update pheromones
            pheromone *= (1 - self.decay)
            
            for path in paths:
                if path and len(path) < best_length:
                    path_length = len(path)
                    if path[-1] == end:
                        best_length = path_length
                        best_path = path
                    
                    # Add pheromone to path
                    pheromone_amount = 1.0 / path_length
                    for i in range(len(path) - 1):
                        pheromone[path[i]-1][path[i+1]-1] += pheromone_amount
        
        return best_path if best_path else []
    
    def _simulate_ants(self, start: Tuple[int, int], 
                      end: Tuple[int, int], 
                      pheromone: np.ndarray) -> List[List[int]]:
        paths = []
        for _ in range(self.n_ants):
            path = self._generate_path(start, end, pheromone)
            paths.append(path)
        return paths
    
    def _generate_path(self, start: Tuple[int, int], 
                      end: Tuple[int, int], 
                      pheromone: np.ndarray) -> List[int]:
        current = start
        path = [current[0] * self.cols + current[1] + 1]
        
        while current != end and len(path) < self.rows * self.cols:
            next_pos = self._select_next(current, path, pheromone, end)
            if not next_pos:
                break
            current = next_pos
            path.append(current[0] * self.cols + current[1] + 1)
        
        return path
    
    def _select_next(self, current: Tuple[int, int], 
                    path: List[int], 
                    pheromone: np.ndarray, 
                    end: Tuple[int, int]) -> Tuple[int, int]:
        neighbors = self._get_valid_neighbors(current, path)
        if not neighbors:
            return None
        
        # Calculate probabilities
        current_idx = current[0] * self.cols + current[1]
        pheromone_values = [pheromone[current_idx][n[0] * self.cols + n[1]] 
                           for n in neighbors]
        heuristic_values = [1.0 / (abs(end[0]-n[0]) + abs(end[1]-n[1]) + 0.1) 
                           for n in neighbors]
        
        probabilities = [(p ** self.alpha) * (h ** self.beta) 
                        for p, h in zip(pheromone_values, heuristic_values)]
        
        total = sum(probabilities)
        if total == 0:
            return random.choice(neighbors)
        
        probabilities = [p/total for p in probabilities]
        return neighbors[np.random.choice(len(neighbors), p=probabilities)]
    
    def _get_valid_neighbors(self, pos: Tuple[int, int], 
                           path: List[int]) -> List[Tuple[int, int]]:
        neighbors = []
        for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
            new_row, new_col = pos[0] + dr, pos[1] + dc
            if (0 <= new_row < self.rows and 
                0 <= new_col < self.cols and 
                new_row * self.cols + new_col + 1 not in path):
                neighbors.append((new_row, new_col))
        return neighbors