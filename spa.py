# spa.py
from collections import deque  # Import for efficient queue operations
import pygame
import sys

def find_shortest_path(start, end, rows=6, cols=6):
    def number_to_coord(num):
        """
        Converts a number to grid coordinates (row, col)
        """
        num -= 1  # Convert to 0-based indexing
        return (num // cols, num % cols)
    
    def coord_to_number(row, col):
        """
        Converts grid coordinates back to number
        """
        return row * cols + col + 1
    
    def get_neighbors(row, col):
        """
        Returns list of valid adjacent positions from current position
        """
        neighbors = []
        if row > 0:  # Up
            neighbors.append((row - 1, col))
        if row < rows - 1:  # Down
            neighbors.append((row + 1, col))
        if col > 0:  # Left
            neighbors.append((row, col - 1))
        if col < cols - 1:  # Right
            neighbors.append((row, col + 1))
        return neighbors
    
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
    
    return None  # Return None if no path is found

class PathFinderApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 600))
        pygame.display.set_caption("Path Finder")
        
        self.rows = 6
        self.cols = 6
        self.start_point = 1
        self.end_point = 36
        
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.input_active = None
        self.start_input = ""
        self.end_input = ""
        
        self.create_widgets()
    
    def create_widgets(self):
        self.screen.fill((255, 255, 255))
        
        self.draw_grid()
        
        self.start_input_box = self.draw_input_box(self.start_input, 150, 10)
        self.end_input_box = self.draw_input_box(self.end_input, 450, 10)
        
        self.find_button_rect, _ = self.draw_button("Find Path", 250, 50)
        
        self.rows_increase_button, _ = self.draw_button("↑", 200, 90)
        self.rows_decrease_button, _ = self.draw_button("↓", 250, 90)
        
        self.cols_increase_button, _ = self.draw_button("↑", 500, 90)
        self.cols_decrease_button, _ = self.draw_button("↓", 550, 90)
        
        self.draw_text("Start Point:", 10, 10)
        self.draw_text("End Point:", 310, 10)
        self.draw_text("Rows:", 10, 100)
        self.draw_text(str(self.rows), 150, 100)
        self.draw_text("Cols:", 310, 100)
        self.draw_text(str(self.cols), 450, 100)
        
        pygame.display.flip()
    
    def draw_text(self, text, x, y):
        text_surface = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(text_surface, (x, y))
    
    def draw_input_box(self, text, x, y):
        input_box = pygame.Rect(x, y, 140, 32)
        pygame.draw.rect(self.screen, (0, 0, 0), input_box, 2)
        text_surface = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(text_surface, (x + 5, y + 5))
        return input_box
    
    def draw_button(self, text, x, y, callback=None):
        button_rect = pygame.Rect(x, y, 100, 32)
        pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 2)
        text_surface = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(text_surface, (x + 5, y + 5))
        return button_rect, callback
    
    def increase_rows(self):
        self.rows += 1
        self.create_widgets()
    
    def decrease_rows(self):
        if self.rows > 1:
            self.rows -= 1
            self.create_widgets()
    
    def increase_cols(self):
        self.cols += 1
        self.create_widgets()
    
    def decrease_cols(self):
        if self.cols > 1:
            self.cols -= 1
            self.create_widgets()
    
    def draw_grid(self):
        cell_width = 400 // self.cols
        cell_height = 400 // self.rows
        
        for i in range(self.rows):
            for j in range(self.cols):
                x1 = j * cell_width + 100
                y1 = i * cell_height + 150
                x2 = x1 + cell_width
                y2 = y1 + cell_height
                pygame.draw.rect(self.screen, (0, 0, 0), (x1, y1, cell_width, cell_height), 1)
    
    def find_path(self):
        try:
            self.start_point = int(self.start_input)
            self.end_point = int(self.end_input)
        except ValueError:
            print("Invalid Input: Please enter valid start and end points.")
            return
        
        path = find_shortest_path(self.start_point, self.end_point, self.rows, self.cols)
        if path:
            self.draw_path(path)
            print(" -> ".join(map(str, path)))
        else:
            print("No path found between the given points.")
    
    def draw_path(self, path):
        self.create_widgets()
        cell_width = 400 // self.cols
        cell_height = 400 // self.rows
        
        for point in path:
            row, col = divmod(point - 1, self.cols)
            x1 = col * cell_width + 100
            y1 = row * cell_height + 150
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            pygame.draw.rect(self.screen, (255, 255, 0), (x1, y1, cell_width, cell_height))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.input_active == "start":
                            self.start_input = ""
                        elif self.input_active == "end":
                            self.end_input = ""
                        self.input_active = None
                        if self.start_input_box.collidepoint(event.pos):
                            self.input_active = "start"
                        elif self.end_input_box.collidepoint(event.pos):
                            self.input_active = "end"
                        elif self.find_button_rect.collidepoint(event.pos):
                            self.find_path()
                        elif self.rows_increase_button.collidepoint(event.pos):
                            self.increase_rows()
                        elif self.rows_decrease_button.collidepoint(event.pos):
                            self.decrease_rows()
                        elif self.cols_increase_button.collidepoint(event.pos):
                            self.increase_cols()
                        elif self.cols_decrease_button.collidepoint(event.pos):
                            self.decrease_cols()
                elif event.type == pygame.KEYDOWN:
                    if self.input_active == "start":
                        if event.key == pygame.K_BACKSPACE:
                            self.start_input = self.start_input[:-1]
                        else:
                            self.start_input += event.unicode
                    elif self.input_active == "end":
                        if event.key == pygame.K_BACKSPACE:
                            self.end_input = self.end_input[:-1]
                        else:
                            self.end_input += event.unicode
                    self.create_widgets()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = PathFinderApp()
    app.run()