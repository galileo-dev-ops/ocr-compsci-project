# spa.py
from collections import deque
import itertools
import heapq

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
    
    def nearest_neighbor(start, points):
        unvisited = set(points)
        current = start
        path = [current]
        while unvisited:
            next_point = min(unvisited, key=lambda point: len(all_paths[(current, point)]))
            path += all_paths[(current, next_point)][1:]
            current = next_point
            unvisited.remove(next_point)
        return path
    
    path = nearest_neighbor(start, points)
    path += all_paths[(path[-1], end)][1:]
    
    return path