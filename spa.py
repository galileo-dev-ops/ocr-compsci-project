import heapq
import random
from database import is_obstacle
import logging, sys
from functools import lru_cache

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class PathFinder:
    def __init__(self, rows=6, cols=6):
        self.rows = rows
        self.cols = cols
        self.initial_mutation_rate = 0.1
        self.mutation_decay = 0.995
        self.path_cache = {}

    def number_to_coord(self, num):
        num -= 1
        return (num // self.cols, num % self.cols)
    
    def coord_to_number(self, row, col):
        return row * self.cols + col + 1
        
    def validate_points(self, points_to_check):
        invalid_points = []
        for point in points_to_check:
            row, col = self.number_to_coord(point)
            if is_obstacle(row, col):
                invalid_points.append(point)
        if invalid_points:
            raise ValueError(
                f"Cannot calculate path: Points {invalid_points} are obstacles. "
                "Please select different points."
            )

    @lru_cache(maxsize=1024)
    def get_neighbors(self, row, col):
        neighbors = set()
        for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
            new_row = row + dr
            new_col = col + dc
            if (0 <= new_row < self.rows and 
                0 <= new_col < self.cols and 
                not is_obstacle(new_row, new_col)):
                neighbors.add((new_row, new_col))
        return neighbors

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def reconstruct_path(self, current, came_from, start):
        path = []
        while current in came_from:
            path.append(self.coord_to_number(*current))
            current = came_from[current]
        path.append(start)
        return path[::-1]

    def find_path(self, start, end):
        cache_key = (start, end)
        if cache_key in self.path_cache:
            return self.path_cache[cache_key]

        path = self.bidirectional_a_star(start, end)
        if path:
            self.path_cache[cache_key] = path
            self.path_cache[(end, start)] = path[::-1]
        return path

    def bidirectional_a_star(self, start, end):
        start_row, start_col = self.number_to_coord(start)
        end_row, end_col = self.number_to_coord(end)
        start_coord = (start_row, start_col)
        end_coord = (end_row, end_col)
        
        forward_open = [(0, start_coord)]
        forward_closed = set()
        forward_came_from = {}
        forward_g_score = {start_coord: 0}
        
        backward_open = [(0, end_coord)]
        backward_closed = set()
        backward_came_from = {}
        backward_g_score = {end_coord: 0}
        
        while forward_open and backward_open:
            # Forward search
            _, current_forward = heapq.heappop(forward_open)
            if current_forward in forward_closed:
                continue
            forward_closed.add(current_forward)
            
            if current_forward in backward_closed:
                return self.reconstruct_bidirectional_path(
                    current_forward, forward_came_from, backward_came_from, start, end)
            
            for neighbor in self.get_neighbors(*current_forward):
                if neighbor in forward_closed:
                    continue
                tentative_g_score = forward_g_score[current_forward] + 1
                if neighbor not in forward_g_score or tentative_g_score < forward_g_score[neighbor]:
                    forward_came_from[neighbor] = current_forward
                    forward_g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + self.heuristic(neighbor, end_coord)
                    heapq.heappush(forward_open, (f_score, neighbor))
            
            # Backward search
            _, current_backward = heapq.heappop(backward_open)
            if current_backward in backward_closed:
                continue
            backward_closed.add(current_backward)
            
            if current_backward in forward_closed:
                return self.reconstruct_bidirectional_path(
                    current_backward, forward_came_from, backward_came_from, start, end)
            
            for neighbor in self.get_neighbors(*current_backward):
                if neighbor in backward_closed:
                    continue
                tentative_g_score = backward_g_score[current_backward] + 1
                if neighbor not in backward_g_score or tentative_g_score < backward_g_score[neighbor]:
                    backward_came_from[neighbor] = current_backward
                    backward_g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + self.heuristic(neighbor, start_coord)
                    heapq.heappush(backward_open, (f_score, neighbor))
        
        return None

    def reconstruct_bidirectional_path(self, meeting_point, forward_came_from, backward_came_from, start, end):
        forward_path = []
        current = meeting_point
        while current in forward_came_from:
            forward_path.append(self.coord_to_number(*current))
            current = forward_came_from[current]
        forward_path.append(start)
        forward_path.reverse()
        
        backward_path = []
        current = meeting_point
        while current in backward_came_from:
            current = backward_came_from[current]
            backward_path.append(self.coord_to_number(*current))
        
        return forward_path + backward_path

    def find_shortest_path(self, start, end, points):
        self.validate_points([start, end] + points)
        
        if not points:
            return self.find_path(start, end)
        
        all_points = [start] + points + [end]
        all_paths = {}
        
        # Calculate paths between all points
        for i, point1 in enumerate(all_points):
            for point2 in all_points[i+1:]:
                path = self.find_path(point1, point2)
                if path:
                    all_paths[(point1, point2)] = path
                    all_paths[(point2, point1)] = path[::-1]
                else:
                    raise ValueError(f"No path found between {point1} and {point2}")

        def path_length(path):
            return sum(len(all_paths[(path[i], path[i + 1])]) - 1 
                      for i in range(len(path) - 1))

        def adaptive_mutate(path, generation):
            mutation_rate = self.initial_mutation_rate * (self.mutation_decay ** generation)
            if len(path) > 3 and random.random() < mutation_rate:
                i, j = random.sample(range(1, len(path) - 1), 2)
                path[i], path[j] = path[j], path[i]

        def crossover(parent1, parent2):
            if len(parent1) <= 3:
                return parent1[:]
            
            start, end = sorted(random.sample(range(1, len(parent1) - 1), 2))
            child = [None] * len(parent1)
            child[start:end] = parent1[start:end]
            
            pointer = 0
            for gene in parent2:
                if gene not in child:
                    while pointer < len(child) and child[pointer] is not None:
                        pointer += 1
                    if pointer < len(child):
                        child[pointer] = gene
            return child

        # Genetic algorithm with early stopping
        population_size = max(50, len(points) * 10)
        generations = 500
        patience = 20
        best_fitness = float('inf')
        generations_without_improvement = 0
        
        population = [[start] + random.sample(points, len(points)) + [end] 
                     for _ in range(population_size)]
        
        for generation in range(generations):
            population.sort(key=path_length)
            current_best = path_length(population[0])
            
            if current_best < best_fitness:
                best_fitness = current_best
                generations_without_improvement = 0
            else:
                generations_without_improvement += 1
                
            if generations_without_improvement >= patience:
                logger.info(f"Early stopping at generation {generation}")
                break
                
            next_gen = population[:population_size // 2]
            
            while len(next_gen) < population_size:
                parent1, parent2 = random.sample(next_gen, 2)
                child = crossover(parent1, parent2)
                adaptive_mutate(child, generation)
                next_gen.append(child)
                
            population = next_gen

        best_route = min(population, key=path_length)
        
        # Reconstruct full path
        full_path = []
        for i in range(len(best_route) - 1):
            full_path.extend(all_paths[(best_route[i], best_route[i + 1])][:-1])
        full_path.append(end)
        
        return full_path