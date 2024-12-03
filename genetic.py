import random
from typing import List, Tuple
import numpy as np

class GeneticPathfinder:
    def __init__(self, rows: int = 6, cols: int = 6, 
                 population_size: int = 100, generations: int = 50):
        self.rows = rows
        self.cols = cols
        self.population_size = population_size
        self.generations = generations

    def find_path(self, start: int, end: int) -> List[int]:
        population = self._initialize_population(start, end)
        
        for _ in range(self.generations):
            fitness_scores = [self._calculate_fitness(path, end) 
                            for path in population]
            parents = self._select_parents(population, fitness_scores)
            population = self._create_new_generation(parents)
            
            best_path = population[np.argmax(fitness_scores)]
            if end in best_path:
                return self._optimize_path(best_path, end)
        
        return []

    def _initialize_population(self, start: int, end: int) -> List[List[int]]:
        population = []
        for _ in range(self.population_size):
            path = [start]
            current = start
            while current != end and len(path) < self.rows * self.cols:
                neighbors = self._get_valid_neighbors(current)
                current = random.choice(neighbors)
                path.append(current)
            population.append(path)
        return population

    def _calculate_fitness(self, path: List[int], end: int) -> float:
        if end in path:
            return 1.0 / len(path)
        return 1.0 / (self.rows * self.cols)

    def _select_parents(self, population: List[List[int]], 
                       fitness_scores: List[float]) -> List[List[int]]:
        parents = []
        for _ in range(self.population_size // 2):
            idx = np.random.choice(len(population), 
                                 p=np.array(fitness_scores)/sum(fitness_scores))
            parents.append(population[idx])
        return parents

    def _create_new_generation(self, parents: List[List[int]]) -> List[List[int]]:
        new_population = parents.copy()
        while len(new_population) < self.population_size:
            parent1, parent2 = random.sample(parents, 2)
            child = self._crossover(parent1, parent2)
            child = self._mutate(child)
            new_population.append(child)
        return new_population

    def _crossover(self, parent1: List[int], parent2: List[int]) -> List[int]:
        crossover_point = random.randint(1, min(len(parent1), len(parent2)) - 1)
        return parent1[:crossover_point] + parent2[crossover_point:]

    def _mutate(self, path: List[int]) -> List[int]:
        if random.random() < 0.1:
            mutation_point = random.randint(1, len(path) - 1)
            current = path[mutation_point - 1]
            neighbors = self._get_valid_neighbors(current)
            path[mutation_point] = random.choice(neighbors)
        return path

    def _get_valid_neighbors(self, position: int) -> List[int]:
        row = (position - 1) // self.cols
        col = (position - 1) % self.cols
        neighbors = []
        
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                neighbors.append(new_row * self.cols + new_col + 1)
        return neighbors

    def _optimize_path(self, path: List[int], end: int) -> List[int]:
        if end not in path:
            return []
        return path[:path.index(end) + 1]