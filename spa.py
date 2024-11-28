# spa.py
from collections import deque
import tkinter as tk
from tkinter import messagebox
import itertools

def find_shortest_path(start, end, points, rows=6, cols=6):
    # Convert a cell number to (row, col) coordinates
    def number_to_coord(num):
        num -= 1
        return (num // cols, num % cols)
    
    # Convert (row, col) coordinates to a cell number
    def coord_to_number(row, col):
        return row * cols + col + 1
    
    # Get the neighboring cells of a given cell
    def get_neighbors(row, col):
        neighbors = []
        if row > 0:
            neighbors.append((row - 1, col))  # Up
        if row < rows - 1:
            neighbors.append((row + 1, col))  # Down
        if col > 0:
            neighbors.append((row, col - 1))  # Left
        if col < cols - 1:
            neighbors.append((row, col + 1))  # Right
        return neighbors
    
    # Perform Breadth-First Search (BFS) to find the shortest path
    def bfs(start, end):
        # Initialize the queue with the start point and the visited set
        queue = deque([(start, [start])])
        visited = set()
        visited.add(start)
        
        while queue:
            current, path = queue.popleft()
            if current == end:
                return path
            
            row, col = number_to_coord(current)
            for neighbor in get_neighbors(row, col):
                neighbor_num = coord_to_number(*neighbor)
                if neighbor_num not in visited:
                    visited.add(neighbor_num)
                    queue.append((neighbor_num, path + [neighbor_num]))
        
        return None  # Return None if no path is found
    
    # Convert points to coordinates and find the shortest path
    start_coord = number_to_coord(start)
    end_coord = number_to_coord(end)
    points_coords = [number_to_coord(point) for point in points]
    
    # Find the shortest path using BFS
    path = bfs(start, end)
    
    if path is None:
        messagebox.showerror("Error", "No path found")
        return []
    
    return path

# Example usage (if needed for testing)
if __name__ == "__main__":
    start = 1
    end = 36
    points = [2, 3, 4, 5, 6, 7, 8, 9, 10]
    rows = 6
    cols = 6
    path = find_shortest_path(start, end, points, rows, cols)
    print("Shortest path:", path)