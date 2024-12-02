# gui.py
import tkinter as tk
from tkinter import simpledialog, messagebox, Toplevel, Menu
from tkinter import filedialog
from spa import find_shortest_path
import threading
import random
import json
from PIL import Image, ImageDraw
from database import create_database, populate_database, get_item_by_id, get_item, update_item_quantity
import math

class PathFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StockBot")
        
        self.configure_grid()
        self.start_point = 1
        self.end_point = self.rows * self.cols
        self.points = []
        
        create_database()
        populate_database(self.rows, self.cols, self.start_point, self.end_point)
        
        self.create_widgets()
        self.create_menu()
        self.visualization_window = None  # Initialize visualization window attribute
        self.canvas = None  # Initialize canvas attribute
    
    def configure_grid(self):
        self.rows = simpledialog.askinteger("Configuration", "Enter the number of rows:", minvalue=1)
        self.cols = simpledialog.askinteger("Configuration", "Enter the number of columns:", minvalue=1)
        if not self.rows or not self.cols:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for rows and columns.")
            self.root.destroy()
        self.start_point = 1
        self.end_point = self.rows * self.cols
        populate_database(self.rows, self.cols, self.start_point, self.end_point)
    
    def create_widgets(self):
        control_frame = tk.Frame(self.root)
        control_frame.grid(row=0, column=0, padx=10, pady=10)
        
        self.points_label = tk.Label(control_frame, text="Points (comma-separated):")
        self.points_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.points_entry = tk.Entry(control_frame)
        self.points_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.find_button = tk.Button(control_frame, text="Find Path", command=self.start_find_path_thread)
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
        
        self.legend_canvas = tk.Canvas(control_frame, width=200, height=120, bg="white")
        self.legend_canvas.grid(row=3, column=1, padx=5, pady=5, columnspan=2)
        
        self.legend_canvas.create_rectangle(10, 10, 30, 30, outline="black", fill="blue")
        self.legend_canvas.create_text(40, 20, anchor="w", text="Start/End Point", fill="black")
        
        self.legend_canvas.create_rectangle(10, 40, 30, 60, outline="black", fill="yellow")
        self.legend_canvas.create_text(40, 50, anchor="w", text="User Points", fill="black")
        
        self.legend_canvas.create_rectangle(10, 70, 30, 90, outline="black", fill="green")
        self.legend_canvas.create_text(40, 80, anchor="w", text="Path", fill="black")
        
        self.legend_canvas.create_rectangle(10, 100, 30, 120, outline="black", fill="red")
        self.legend_canvas.create_text(40, 110, anchor="w", text="Out of Stock", fill="black")
        
        self.path_output = tk.Text(self.root, height=5, width=50)
        self.path_output.grid(row=1, column=0, padx=10, pady=10)
        
        self.path_distance_label = tk.Label(control_frame, text="Total Path Distance: 0")
        self.path_distance_label.grid(row=4, column=0, padx=5, pady=5, columnspan=3)
        
        self.query_button = tk.Button(control_frame, text="Query ItemID", command=self.query_item_id)
        self.query_button.grid(row=5, column=0, padx=5, pady=5, columnspan=3)
        
        self.update_quantity_button = tk.Button(control_frame, text="Update Quantity", command=self.update_quantity)
        self.update_quantity_button.grid(row=6, column=0, padx=5, pady=5, columnspan=3)
        
        self.export_button = tk.Button(control_frame, text="Export Grid", command=self.export_grid)
        self.export_button.grid(row=7, column=0, padx=5, pady=5, columnspan=3)
    
    def create_menu(self):
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)
        
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Save Configuration", command=self.save_configuration)
        file_menu.add_command(label="Load Configuration", command=self.load_configuration)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Help", command=self.show_help)
        menu_bar.add_cascade(label="Help", menu=help_menu)
    
    def show_help(self):
        help_window = Toplevel(self.root)
        help_window.title("Help")
        help_text = tk.Text(help_window, wrap=tk.WORD, width=80, height=20)
        help_text.pack(expand=True, fill=tk.BOTH)
        help_text.insert(tk.END, """
        Welcome to StockBot!

        This application helps you find the shortest path in a warehouse grid while avoiding out-of-stock items.

        Features:
        - Enter the number of rows and columns to configure the grid.
        - Enter points (comma-separated) to specify the items you want to visit.
        - Click "Find Path" to calculate and visualize the shortest path.
        - Out-of-stock items are highlighted in red and avoided in the path calculation.
        - Start and end points are highlighted in blue.
        - User-specified points are highlighted in yellow.
        - The calculated path is highlighted in green.
        - Query an item by its ID to see its location and quantity.
        - Update the quantity of an item by its ID.
        - Save and load grid configurations.
        - Export the grid and path as an image.

        How to Use:
        1. Configure the grid by entering the number of rows and columns.
        2. Enter the points you want to visit in the "Points" field.
        3. Click "Find Path" to calculate and visualize the shortest path.
        4. Use the "Query ItemID" button to get information about a specific item.
        5. Use the "Update Quantity" button to update the quantity of a specific item.
        6. Use the "Save Configuration" option to save the current grid configuration.
        7. Use the "Load Configuration" option to load a saved grid configuration.
        8. Use the "Export Grid" button to export the grid and path as an image file.

        Thank you for using StockBot!
        """)
        help_text.config(state=tk.DISABLED)
    
    def open_visualization_window(self):
        if self.visualization_window is None or not self.visualization_window.winfo_exists():
            self.visualization_window = Toplevel(self.root)
            self.visualization_window.title("Path Visualization")
            self.canvas = tk.Canvas(self.visualization_window, width=800, height=800, bg="white")
            self.canvas.pack(fill=tk.BOTH, expand=True)
            self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.draw_grid()
    
    def draw_grid(self):
        if self.canvas is None:
            return
        self.canvas.delete("all")
        cell_width = min(800 // self.cols, 800 // self.rows)
        cell_height = cell_width
        font_size = max(8, cell_width // 3)
        
        for i in range(self.rows):
            for j in range(self.cols):
                x1 = j * cell_width
                y1 = i * cell_height
                x2 = x1 + cell_width
                y2 = y1 + cell_height
                item = get_item(i, j)
                if item and item[1] == 0:
                    color = "red"
                else:
                    color = "white"
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color)
                self.canvas.create_text(x1 + cell_width / 2, y1 + cell_height / 2, text=str(i * self.cols + j + 1), fill="green", font=("Arial", font_size))
    
    def on_canvas_click(self, event):
        cell_width = min(800 // self.cols, 800 // self.rows)
        cell_height = cell_width
        col = event.x // cell_width
        row = event.y // cell_height
        self.show_item_info(row, col)
    
    def show_item_info(self, row, col):
        item = get_item(row, col)
        if item:
            item_id, quantity = item
            messagebox.showinfo("Item Info", f"ItemID: {item_id}\nQuantity: {quantity}")
        else:
            messagebox.showinfo("Item Info", "No item found.")
    
    def query_item_id(self):
        item_id = simpledialog.askinteger("Query ItemID", "Enter the ItemID:", minvalue=1)
        if item_id is not None:
            item = get_item_by_id(item_id)
            if item:
                row, col, quantity = item
                messagebox.showinfo("Item Info", f"ItemID: {item_id}\nRow: {row}\nCol: {col}\nQuantity: {quantity}")
            else:
                messagebox.showinfo("Item Info", "No item found.")
    
    def update_quantity(self):
        item_id = simpledialog.askinteger("Update Quantity", "Enter the ItemID:", minvalue=1)
        if item_id is not None:
            quantity = simpledialog.askinteger("Update Quantity", "Enter the new quantity:", minvalue=0)
            if quantity is not None:
                update_item_quantity(item_id, quantity)
                messagebox.showinfo("Update Quantity", f"ItemID: {item_id}\nNew Quantity: {quantity}")
    
    def highlight_point(self, point, color):
        if self.canvas is None:
            return
        cell_width = min(800 // self.cols, 800 // self.rows)
        cell_height = cell_width
        font_size = max(8, cell_width // 3)
        row, col = divmod(point - 1, self.cols)
        x1 = col * cell_width
        y1 = row * cell_height
        x2 = x1 + cell_width
        y2 = y1 + cell_height
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color)
        self.canvas.create_text(x1 + cell_width / 2, y1 + cell_height / 2, text=str(point), fill="green", font=("Arial", font_size))
    
    def draw_arrow(self, start_point, end_point):
        if self.canvas is None:
            return
        cell_width = min(800 // self.cols, 800 // self.rows)
        cell_height = cell_width
        
        start_row, start_col = divmod(start_point - 1, self.cols)
        end_row, end_col = divmod(end_point - 1, self.cols)
        
        start_x = start_col * cell_width + cell_width / 2
        start_y = start_row * cell_height + cell_height / 2
        end_x = end_col * cell_width + cell_width / 2
        end_y = end_row * cell_height + cell_height / 2
        
        self.canvas.create_line(start_x, start_y, end_x, end_y, arrow=tk.LAST, fill="black")
    
    def start_find_path_thread(self):
        threading.Thread(target=self.find_path).start()
    

    def find_path(self):
        try:
            points = list(map(int, self.points_entry.get().split(',')))
            self.points = points
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid points.")
            return

        # Check if start or end points are in the user input
        if self.start_point in self.points or self.end_point in self.points:
            messagebox.showerror("Invalid Input", "You have inputted a start and/or end point. Please remove it!")
            return

        # Remove out-of-stock items from the points list
        valid_points = []
        self.open_visualization_window()
        for point in self.points:
            row, col = divmod(point - 1, self.cols)
            item = get_item(row, col)
            if item and item[1] == 0:
                self.highlight_point(point, "red")
            else:
                valid_points.append(point)

        try:
            path = find_shortest_path(self.start_point, self.end_point, valid_points, self.rows, self.cols)
            if path:
                self.path = path  # Store the path in an instance variable
                self.animate_path(path, valid_points)
                self.path_output.delete(1.0, tk.END)
                self.path_output.insert(tk.END, " -> ".join(map(str, path)))
                self.path_distance_label.config(text=f"Total Path Distance: {self.calculate_path_cost(path)}")
            else:
                messagebox.showinfo("No Path", "No path found between the given points.")
        except ValueError as e:
            messagebox.showerror("Path Error", str(e))
        
    def animate_path(self, path, valid_points):
        self.draw_grid()
        cell_width = min(800 // self.cols, 800 // self.rows)
        cell_height = cell_width
        
        for i in range(len(path) - 1):
            self.draw_arrow(path[i], path[i + 1])
            self.root.update()
            self.root.after(100)  # Adjust the delay for animation speed
        
        for point in path:
            row, col = divmod(point - 1, self.cols)
            item = get_item(row, col)
            if item and item[1] == 0:
                self.highlight_point(point, "red")
            else:
                x1 = col * cell_width
                y1 = row * cell_height
                x2 = x1 + cell_width
                y2 = y1 + cell_height
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="green")
                self.canvas.create_text(x1 + cell_width / 2, y1 + cell_height / 2, text=str(point), fill="green")
        
        # Highlight start and end points
        self.highlight_point(self.start_point, "blue")
        self.highlight_point(self.end_point, "blue")
        
        # Highlight user input points
        for point in self.points:
            if point in valid_points:
                self.highlight_point(point, "yellow")
    
    def calculate_path_cost(self, path):
        # Calculate the total cost of the path (e.g., total distance)
        return len(path) - 1
    
    def save_configuration(self):
        config = {
            "rows": self.rows,
            "cols": self.cols,
            "points": self.points,
            "items": []
        }
        for i in range(self.rows):
            for j in range(self.cols):
                item = get_item(i, j)
                if item:
                    item_id, quantity = item
                    config["items"].append({"row": i, "col": j, "item_id": item_id, "quantity": quantity})
        
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "w") as file:
                json.dump(config, file)
            messagebox.showinfo("Save Configuration", "Configuration saved successfully.")
    
    def load_configuration(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "r") as file:
                config = json.load(file)
            
            self.rows = config["rows"]
            self.cols = config["cols"]
            self.points = config["points"]
            self.rows_value.config(text=str(self.rows))
            self.cols_value.config(text=str(self.cols))
            
            create_database()
            for item in config["items"]:
                update_item_quantity(item["item_id"], item["quantity"])
            
            self.draw_grid()
            messagebox.showinfo("Load Configuration", "Configuration loaded successfully.")
    
    def export_grid(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if not file_path:
            return
        
        cell_width = min(800 // self.cols, 800 // self.rows)
        cell_height = cell_width
        img_width = self.cols * cell_width
        img_height = self.rows * cell_height
        
        image = Image.new("RGB", (img_width, img_height), "white")
        draw = ImageDraw.Draw(image)
        
        for i in range(self.rows):
            for j in range(self.cols):
                x1 = j * cell_width
                y1 = i * cell_height
                x2 = x1 + cell_width
                y2 = y1 + cell_height
                item = get_item(i, j)
                if item and item[1] == 0:
                    color = "red"
                else:
                    color = "white"
                draw.rectangle([x1, y1, x2, y2], outline="black", fill=color)
                draw.text((x1 + cell_width / 2, y1 + cell_height / 2), str(i * self.cols + j + 1), fill="green")
        
        # Highlight the path with arrows
        if hasattr(self, 'path') and self.path:
            for i in range(len(self.path) - 1):
                start_point = self.path[i]
                end_point = self.path[i + 1]
                start_row, start_col = divmod(start_point - 1, self.cols)
                end_row, end_col = divmod(end_point - 1, self.cols)
                
                start_x = start_col * cell_width + cell_width / 2
                start_y = start_row * cell_height + cell_height / 2
                end_x = end_col * cell_width + cell_width / 2
                end_y = end_row * cell_height + cell_height / 2
                
                draw.line([start_x, start_y, end_x, end_y], fill="black", width=2)
                
                # Draw arrowhead
                arrow_size = 10
                angle = math.atan2(end_y - start_y, end_x - start_x)
                arrow_x1 = end_x - arrow_size * math.cos(angle - math.pi / 6)
                arrow_y1 = end_y - arrow_size * math.sin(angle - math.pi / 6)
                arrow_x2 = end_x - arrow_size * math.cos(angle + math.pi / 6)
                arrow_y2 = end_y - arrow_size * math.sin(angle + math.pi / 6)
                draw.polygon([end_x, end_y, arrow_x1, arrow_y1, arrow_x2, arrow_y2], fill="black")
        
        # Highlight start and end points
        if hasattr(self, 'start_point') and self.start_point:
            row, col = divmod(self.start_point - 1, self.cols)
            x1 = col * cell_width
            y1 = row * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            draw.rectangle([x1, y1, x2, y2], outline="black", fill="blue")
            draw.text((x1 + cell_width / 2, y1 + cell_height / 2), str(self.start_point), fill="green")
        
        if hasattr(self, 'end_point') and self.end_point:
            row, col = divmod(self.end_point - 1, self.cols)
            x1 = col * cell_width
            y1 = row * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            draw.rectangle([x1, y1, x2, y2], outline="black", fill="blue")
            draw.text((x1 + cell_width / 2, y1 + cell_height / 2), str(self.end_point), fill="green")
        
        # Highlight user input points
        for point in self.points:
            row, col = divmod(point - 1, self.cols)
            x1 = col * cell_width
            y1 = row * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            draw.rectangle([x1, y1, x2, y2], outline="black", fill="yellow")
            draw.text((x1 + cell_width / 2, y1 + cell_height / 2), str(point), fill="green")
        
        image.save(file_path)
        messagebox.showinfo("Export Grid", "Grid exported successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PathFinderApp(root)
    root.mainloop()