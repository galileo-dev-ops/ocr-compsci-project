# gui.py
import tkinter as tk
from tkinter import simpledialog, messagebox
from spa import find_shortest_path

class PathFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StockBot")
        
        self.configure_grid()
        self.start_point = 1
        self.end_point = self.rows * self.cols
        self.points = []
        
        self.create_widgets()
    
    def configure_grid(self):
        self.rows = simpledialog.askinteger("Configuration", "Enter the number of rows:", minvalue=1)
        self.cols = simpledialog.askinteger("Configuration", "Enter the number of columns:", minvalue=1)
        if not self.rows or not self.cols:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for rows and columns.")
            self.root.destroy()
    
    def create_widgets(self):
        control_frame = tk.Frame(self.root)
        control_frame.grid(row=0, column=0, padx=10, pady=10)
        
        self.points_label = tk.Label(control_frame, text="Points (comma-separated):")
        self.points_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.points_entry = tk.Entry(control_frame)
        self.points_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.find_button = tk.Button(control_frame, text="Find Path", command=self.find_path)
        self.find_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.rows_label = tk.Label(control_frame, text="Rows:")
        self.rows_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.rows_value = tk.Label(control_frame, text=str(self.rows))
        self.rows_value.grid(row=1, column=1, padx=5, pady=5)
        
        self.cols_label = tk.Label(control_frame, text="Cols:")
        self.cols_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.cols_value = tk.Label(control_frame, text=str(self.cols))
        self.cols_value.grid(row=2, column=1, padx=5, pady=5)
        
        self.legend_label = tk.Label(control_frame, text="Legend:")
        self.legend_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        
        self.legend_canvas = tk.Canvas(control_frame, width=200, height=100, bg="white")
        self.legend_canvas.grid(row=3, column=1, padx=5, pady=5, columnspan=2)
        
        self.legend_canvas.create_rectangle(10, 10, 30, 30, outline="black", fill="blue")
        self.legend_canvas.create_text(40, 20, anchor="w", text="Start Point", fill="black")
        
        self.legend_canvas.create_rectangle(10, 40, 30, 60, outline="black", fill="red")
        self.legend_canvas.create_text(40, 50, anchor="w", text="End Point", fill="black")
        
        self.legend_canvas.create_rectangle(10, 70, 30, 90, outline="black", fill="orange")
        self.legend_canvas.create_text(40, 80, anchor="w", text="User Points", fill="black")
        
        self.canvas = tk.Canvas(self.root, width=400, height=400, bg="white")
        self.canvas.grid(row=1, column=0, padx=10, pady=10)
        
        self.path_output = tk.Text(self.root, height=5, width=50)
        self.path_output.grid(row=2, column=0, padx=10, pady=10)
        
        self.path_distance_label = tk.Label(control_frame, text="Total Path Distance: 0")
        self.path_distance_label.grid(row=4, column=0, padx=5, pady=5, columnspan=3)
        
        self.draw_grid()
    
    def draw_grid(self):
        self.canvas.delete("all")
        cell_width = 400 // self.cols
        cell_height = 400 // self.rows
        
        for i in range(self.rows):
            for j in range(self.cols):
                x1 = j * cell_width
                y1 = i * cell_height
                x2 = x1 + cell_width
                y2 = y1 + cell_height
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black")
                self.canvas.create_text(x1 + cell_width / 2, y1 + cell_height / 2, text=str(i * self.cols + j + 1), fill="green")
    
    def highlight_point(self, point, color):
        cell_width = 400 // self.cols
        cell_height = 400 // self.rows
        row, col = divmod(point - 1, self.cols)
        x1 = col * cell_width
        y1 = row * cell_height
        x2 = x1 + cell_width
        y2 = y1 + cell_height
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color)
        self.canvas.create_text(x1 + cell_width / 2, y1 + cell_height / 2, text=str(point), fill="green")
    
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
        self.draw_grid()
        cell_width = 400 // self.cols
        cell_height = 400 // self.rows
        
        for point in path:
            row, col = divmod(point - 1, self.cols)
            x1 = col * cell_width
            y1 = row * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="green")
            self.canvas.create_text(x1 + cell_width / 2, y1 + cell_height / 2, text=str(point), fill="green")
        
        # Highlight start point
        self.highlight_point(self.start_point, "blue")
        
        # Highlight end point
        self.highlight_point(self.end_point, "red")
        
        # Highlight user input points
        for point in self.points:
            self.highlight_point(point, "orange")

if __name__ == "__main__":
    root = tk.Tk()
    app = PathFinderApp(root)
    root.mainloop()