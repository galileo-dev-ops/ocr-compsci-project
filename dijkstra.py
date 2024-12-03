from typing import List, Dict, Tuple
import heapq

class DijkstraPathfinder:
    def __init__(self, rows: int = 6, cols: int = 6):
        self.rows = rows
        self.cols = cols
    
    def find_path(self, start: int, end: int) -> List[int]:
        def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
            row, col = pos
            directions = [(0,1), (1,0), (0,-1), (-1,0)]
            return [(row + dr, col + dc) for dr, dc in directions
                    if 0 <= row + dr < self.rows and 0 <= col + dc < self.cols]

        start_pos = ((start - 1) // self.cols, (start - 1) % self.cols)
        end_pos = ((end - 1) // self.cols, (end - 1) % self.cols)
        
        distances = {start_pos: 0}
        pq = [(0, start_pos)]
        previous = {start_pos: None}
        
        while pq:
            dist, current = heapq.heappop(pq)
            
            if current == end_pos:
                path = []
                while current:
                    path.append(current[0] * self.cols + current[1] + 1)
                    current = previous[current]
                return path[::-1]
            
            for next_pos in get_neighbors(current):
                new_dist = dist + 1
                if next_pos not in distances or new_dist < distances[next_pos]:
                    distances[next_pos] = new_dist
                    previous[next_pos] = current
                    heapq.heappush(pq, (new_dist, next_pos))
        return []