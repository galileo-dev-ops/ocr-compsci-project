# gui.py
import tkinter as tk
from tkinter import simpledialog, messagebox
from spa import find_shortest_path

class PathFinderApp:
    def __init__(self, root):
        # Initialize the main application window
        self.root = root
        self.root.title("StockBot")  # Set the window title
        
        self.configure_grid()  # Configure the grid dimensions
        self.start_point = 1  # Initialize the start point
        self.end_point = self.rows * self.cols  # Initialize the end point based on grid size
        self.points = []  # Initialize an empty list to store user input points
        
        self.create_widgets()  # Create the UI elements
    
    def configure_grid(self):
        # Prompt the user to enter the number of rows
        self.rows = simpledialog.askinteger("Configuration", "Enter the number of rows:", minvalue=1)
        # Prompt the user to enter the number of columns
        self.cols = simpledialog.askinteger("Configuration", "Enter the number of columns:", minvalue=1)
        # Check if the user entered valid numbers
        if not self.rows or not self.cols:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for rows and columns.")
            self.root.destroy()

def create_widgets(self):
    # Create a frame widget within the root window to hold control elements
    control_frame = tk.Frame(self.root)
    control_frame.grid(row=0, column=0, padx=10, pady=10)
    
    # Create and place a label for points input
    self.points_label = tk.Label(control_frame, text="Points (comma-separated):")
    self.points_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    
    # Create and place an entry widget for points input
    self.points_entry = tk.Entry(control_frame)
    self.points_entry.grid(row=0, column=1, padx=5, pady=5)
    
    # Create and place a button to find the path
    self.find_button = tk.Button(control_frame, text="Find Path", command=self.find_path)
    self.find_button.grid(row=0, column=2, padx=5, pady=5)
    
    # Create and place a label for displaying the number of rows
    self.rows_label = tk.Label(control_frame, text="Rows:")
    self.rows_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    self.rows_value = tk.Label(control_frame, text=str(self.rows))
    self.rows_value.grid(row=1, column=1, padx=5, pady=5)
    
    # Create and place a label for displaying the number of columns
    self.cols_label = tk.Label(control_frame, text="Cols:")
    self.cols_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
    self.cols_value = tk.Label(control_frame, text=str(self.cols))
    self.cols_value.grid(row=2, column=1, padx=5, pady=5)
    
    # Create and place a label for the legend
    self.legend_label = tk.Label(control_frame, text="Legend:")
    self.legend_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
    
    # Create and place a canvas widget for drawing the grid and paths
    self.canvas = tk.Canvas(self.root, width=self.cols * 20, height=self.rows * 20, bg="white")
    self.canvas.grid(row=1, column=0, padx=10, pady=10)
    
    # Draw the grid on the canvas
    self.draw_grid()

def draw_grid(self):
    # Draw the grid lines on the canvas
    for i in range(self.rows):
        for j in range(self.cols):
            x1 = j * 20
            y1 = i * 20
            x2 = x1 + 20
            y2 = y1 + 20
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="black")

def highlight_point(self, point, color):
    # Highlight a specific point on the grid with the given color
    row = (point - 1) // self.cols
    col = (point - 1) % self.cols
    x1 = col * 20
    y1 = row * 20
    x2 = x1 + 20
    y2 = y1 + 20
    self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2)

def find_path(self):
    # Find the shortest path using the provided points
    points = self.points_entry.get().split(',')
    points = [int(point.strip()) for point in points if point.strip().isdigit()]
    self.points = points
    
    # Clear previous highlights
    self.canvas.delete("all")
    self.draw_grid()
    
    # Highlight the start and end points
    self.highlight_point(self.start_point, "blue")
    self.highlight_point(self.end_point, "red")
    
    # Highlight user input points
    for point in self.points:
        self.highlight_point(point, "orange")
    
    # Find and highlight the shortest path
    path = find_shortest_path(self.start_point, self.end_point, self.points, self.rows, self.cols)
    for point in path:
        self.highlight_point(point, "green")

if __name__ == "__main__":
    # Create the main window and run the application
    root = tk.Tk()
    app = PathFinderApp(root)
    root.mainloop()