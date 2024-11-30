# spa.py
from collections import deque
import itertools

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
    
    def bfs(start, end):
        start_row, start_col = number_to_coord(start)
        end_row, end_col = number_to_coord(end)
        queue = deque([(start_row, start_col, [start])])
        visited = set()
        
        while queue:
            current_row, current_col, current_path = queue.popleft()
            
            if (current_row, current_col) in visited:
                continue
            
            visited.add((current_row, current_col))
            
            if current_row == end_row and current_col == end_col:
                return current_path
            
            for neighbor in get_neighbors(current_row, current_col):
                next_row, next_col = neighbor
                next_num = coord_to_number(next_row, next_col)
                queue.append((next_row, next_col, current_path + [next_num]))
        
        return None
    
    all_points = [start] + points + [end]
    all_paths = {}
    
    for i, point1 in enumerate(all_points):
        for point2 in all_points[i+1:]:
            path = bfs(point1, point2)
            if path:
                all_paths[(point1, point2)] = path
                all_paths[(point2, point1)] = path[::-1]
    
    min_path = None
    min_length = float('inf')
    
    for perm in itertools.permutations(points):
        current_path = [start]
        current_length = 0
        current_point = start
        
        for point in perm:
            current_path += all_paths[(current_point, point)][1:]
            current_length += len(all_paths[(current_point, point)]) - 1
            current_point = point
        
        current_path += all_paths[(current_point, end)][1:]
        current_length += len(all_paths[(current_point, end)]) - 1
        
        if current_length < min_length:
            min_length = current_length
            min_path = current_path
    
    return min_path