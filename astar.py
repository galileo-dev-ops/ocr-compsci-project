from typing import Tuple, List, Dict
import heapq

class AStarPathfinder:
    def __init__(self, rows: int = 6, cols: int = 6):
        self.rows = rows
        self.cols = cols

    def find_path(self, start: int, end: int) -> List[int]:
        def manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
            row, col = pos
            return [(row + dr, col + dc) for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]
                    if 0 <= row + dr < self.rows and 0 <= col + dc < self.cols]

        start_pos = ((start - 1) // self.cols, (start - 1) % self.cols)
        end_pos = ((end - 1) // self.cols, (end - 1) % self.cols)
        
        open_set = [(manhattan_distance(start_pos, end_pos), start_pos)]
        came_from: Dict = {start_pos: None}
        g_score = {start_pos: 0}
        
        while open_set:
            _, current = heapq.heappop(open_set)
            if current == end_pos:
                path = []
                while current:
                    path.append(current[0] * self.cols + current[1] + 1)
                    current = came_from[current]
                return path[::-1]
            
            for neighbor in get_neighbors(current):
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + manhattan_distance(neighbor, end_pos)
                    heapq.heappush(open_set, (f_score, neighbor))
        return []