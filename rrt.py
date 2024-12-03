from typing import List, Tuple
import random
import math

class RRTPathfinder:
    def __init__(self, rows: int = 6, cols: int = 6, max_iterations: int = 1000):
        self.rows = rows
        self.cols = cols
        self.max_iterations = max_iterations
    
    def find_path(self, start: int, end: int) -> List[int]:
        def coord_to_num(pos: Tuple[int, int]) -> int:
            return pos[0] * self.cols + pos[1] + 1
            
        def distance(a: Tuple[int, int], b: Tuple[int, int]) -> float:
            return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
        
        start_pos = ((start - 1) // self.cols, (start - 1) % self.cols)
        end_pos = ((end - 1) // self.cols, (end - 1) % self.cols)
        
        vertices = {start_pos}
        edges = {}
        
        for _ in range(self.max_iterations):
            # Random sample
            if random.random() < 0.1:  # Bias towards goal
                sample = end_pos
            else:
                sample = (random.randint(0, self.rows-1), 
                         random.randint(0, self.cols-1))
            
            # Find nearest vertex
            nearest = min(vertices, key=lambda v: distance(v, sample))
            
            # Create new vertex
            dx = sample[0] - nearest[0]
            dy = sample[1] - nearest[1]
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                dx, dy = dx/dist, dy/dist
                new_pos = (round(nearest[0] + dx), round(nearest[1] + dy))
                
                if (0 <= new_pos[0] < self.rows and 
                    0 <= new_pos[1] < self.cols and 
                    new_pos not in vertices):
                    vertices.add(new_pos)
                    edges[new_pos] = nearest
                    
                    if new_pos == end_pos:
                        # Reconstruct path
                        path = []
                        current = new_pos
                        while current in edges:
                            path.append(coord_to_num(current))
                            current = edges[current]
                        path.append(start)
                        return path[::-1]
        return []