# gui.py
import tkinter as tk
from tkinter import simpledialog, messagebox
from spa import find_shortest_path
import threading

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
        self.find_button = tk.Button(control_frame, text="Find Path", command=self.start_find_path_thread)
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
        self.legend_label.grid(row=3, column=0, padx=5, pady=5, columnspan=3, sticky="ew")
        
        # Create and place labels for the legend items with colored backgrounds
        self.legend_start = tk.Label(control_frame, text="Start Point", bg="blue", fg="white", width=15)
        self.legend_start.grid(row=4, column=0, padx=5, pady=5, columnspan=3, sticky="ew")
        self.legend_end = tk.Label(control_frame, text="End Point", bg="red", fg="white", width=15)
        self.legend_end.grid(row=5, column=0, padx=5, pady=5, columnspan=3, sticky="ew")
        self.legend_user = tk.Label(control_frame, text="User Points", bg="orange", fg="white", width=15)
        self.legend_user.grid(row=6, column=0, padx=5, pady=5, columnspan=3, sticky="ew")
        self.legend_path = tk.Label(control_frame, text="Path", bg="green", fg="white", width=15)
        self.legend_path.grid(row=7, column=0, padx=5, pady=5, columnspan=3, sticky="ew")
        
        # Create and place a text widget for displaying the path output
        self.path_output = tk.Text(control_frame, height=5, width=50)
        self.path_output.grid(row=8, column=0, columnspan=3, padx=5, pady=5)
        
        # Create and place a label for displaying the path distance
        self.path_distance_label = tk.Label(control_frame, text="Total Path Distance: 0")
        self.path_distance_label.grid(row=9, column=0, columnspan=3, padx=5, pady=5)
    
    def start_find_path_thread(self):
        threading.Thread(target=self.find_path).start()
    
    def find_path(self):
        try:
            points = list(map(int, self.points_entry.get().split(',')))
            self.points = points
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid points.")
            return
        
        path = find_shortest_path(self.start_point, self.end_point, self.points, self.rows, self.cols)
        if path:
            self.draw_path(path)
            self.path_output.delete(1.0, tk.END)
            self.path_output.insert(tk.END, " -> ".join(map(str, path)))
            self.path_distance_label.config(text=f"Total Path Distance: {len(path) - 1}")
        else:
            messagebox.showinfo("No Path", "No path found between the given points.")
    
    def draw_path(self, path):
        # Create a new window for the grid visualization
        grid_window = tk.Toplevel(self.root)
        grid_window.title("Grid Visualization")
        
        # Calculate the size of the new window based on the number of rows and columns
        window_width = min(800, self.cols * 20)
        window_height = min(800, self.rows * 20)
        grid_window.geometry(f"{window_width}x{window_height}")
        
        # Create a canvas widget for drawing the grid and paths
        self.canvas = tk.Canvas(grid_window, width=window_width, height=window_height, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw the grid on the canvas
        self.draw_grid()
        
        cell_width = window_width // self.cols
        cell_height = window_height // self.rows
        
        for point in path:
            row, col = divmod(point - 1, self.cols)
            x1 = col * cell_width
            y1 = row * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="green")
            self.canvas.create_text(x1 + cell_width / 2, y1 + cell_height / 2, text=str(point), fill="white")
        
        # Highlight start point
        self.highlight_point(self.start_point, "blue", fill=True)
        
        # Highlight end point
        self.highlight_point(self.end_point, "red", fill=True)
        
        # Highlight user input points
        for point in self.points:
            self.highlight_point(point, "orange", fill=False)
    
    def draw_grid(self):
        # Draw the grid lines on the canvas
        for i in range(self.rows):
            for j in range(self.cols):
                x1 = j * 20
                y1 = i * 20
                x2 = x1 + 20
                y2 = y1 + 20
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black")

    def highlight_point(self, point, color, fill=False):
        # Highlight a specific point on the grid with the given color
        row = (point - 1) // self.cols
        col = (point - 1) % self.cols
        cell_width = self.canvas.winfo_width() // self.cols
        cell_height = self.canvas.winfo_height() // self.rows
        x1 = col * cell_width
        y1 = row * cell_height
        x2 = x1 + cell_width
        y2 = y1 + cell_height
        if fill:
            self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, fill=color)
        else:
            self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2)

if __name__ == "__main__":
    # Create the main window and run the application
    root = tk.Tk()
    app = PathFinderApp(root)
    root.mainloop()