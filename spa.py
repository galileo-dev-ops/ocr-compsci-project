# spa.py
from collections import deque
import itertools
import heapq
import random

def find_shortest_path(start, end, points, rows=6, cols=6):
    def number_to_coord(num):
        num -= 1
        return (num // cols, num % cols)
    
    def coord_to_number(row, col):
        return row * cols + col + 1
    
    def get_neighbors(row, col):
        neighbors = []
        if row > 0:
            neighbors.append((row - 1, col))
        if row < rows - 1:
            neighbors.append((row + 1, col))
        if col > 0:
            neighbors.append((row, col - 1))
        if col < cols - 1:
            neighbors.append((row, col + 1))
        return neighbors
    
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def a_star(start, end):
        start_row, start_col = number_to_coord(start)
        end_row, end_col = number_to_coord(end)
        start_coord = (start_row, start_col)
        end_coord = (end_row, end_col)
        
        open_set = []
        heapq.heappush(open_set, (0, start_coord))
        came_from = {}
        g_score = {start_coord: 0}
        f_score = {start_coord: heuristic(start_coord, end_coord)}
        
        while open_set:
            _, current = heapq.heappop(open_set)
            
            if current == end_coord:
                path = []
                while current in came_from:
                    path.append(coord_to_number(*current))
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path
            
            for neighbor in get_neighbors(*current):
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, end_coord)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return None
    
    all_points = [start] + points + [end]
    all_paths = {}
    
    for i, point1 in enumerate(all_points):
        for point2 in all_points[i+1:]:
            path = a_star(point1, point2)
            if path:
                all_paths[(point1, point2)] = path
                all_paths[(point2, point1)] = path[::-1]
            else:
                raise ValueError(f"No path found between {point1} and {point2}")
    
    def fitness(path):
        return sum(len(all_paths[(path[i], path[i + 1])]) - 1 for i in range(len(path) - 1))
    
    def mutate(path):
        if len(path) > 3:
            i, j = random.sample(range(1, len(path) - 1), 2)
            path[i], path[j] = path[j], path[i]
    
    def crossover(parent1, parent2):
        if len(parent1) > 3:
            start, end = sorted(random.sample(range(1, len(parent1) - 1), 2))
            child = [None] * len(parent1)
            child[start:end] = parent1[start:end]
            pointer = 0
            for gene in parent2:
                if gene not in child:
                    while child[pointer] is not None:
                        pointer += 1
                    child[pointer] = gene
            return child
        return parent1[:]
    
    def genetic_algorithm(start, points, end, population_size=100, generations=500):
        if len(points) == 0:
            return [start, end]
        
        population_size = max(2, population_size)
        population = [[start] + random.sample(points, len(points)) + [end] for _ in range(population_size)]
        for _ in range(generations):
            population.sort(key=fitness)
            next_generation = population[:population_size // 2]
            for _ in range(population_size // 2):
                parent1, parent2 = random.sample(next_generation, 2)
                child = crossover(parent1, parent2)
                if random.random() < 0.1:
                    mutate(child)
                next_generation.append(child)
            population = next_generation
        return min(population, key=fitness)
    
    path = genetic_algorithm(start, points, end)
    full_path = []
    for i in range(len(path) - 1):
        full_path += all_paths[(path[i], path[i + 1])][:-1]
    full_path.append(end)
    
    return full_path