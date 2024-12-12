import tkinter as tk
from tkinter import simpledialog, messagebox, Toplevel, Menu, Spinbox
from tkinter import filedialog
from spa import PathFinder
import threading
import json
from PIL import Image, ImageDraw
from database import create_database, populate_database, get_item_by_id, get_item, update_item_quantity, is_obstacle, set_obstacle
import math
import logging, sys

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('StockBot')

class PathFinderApp:
    def __init__(self, root):
        logger.debug("Initializing PathFinderApp")
        self.root = root
        self.root.title("StockBot")
        
        self.rows = 1
        self.cols = 1
        self.start_point = 1
        self.end_point = 1
        self.points = []
        
        create_database()
        
        self.visualization_window = None  # Initialize visualization window attribute
        self.canvas = None  # Initialize canvas attribute
        
        self.show_configuration_screen()  # Show configuration screen on startup
    
    def show_configuration_screen(self):
        config_window = Toplevel(self.root)
        config_window.title("Configure Grid")
        
        tk.Label(config_window, text="Rows:").grid(row=0, column=0, padx=10, pady=10)
        self.rows_spinbox = Spinbox(config_window, from_=1, to=100, width=5)
        self.rows_spinbox.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(config_window, text="Columns:").grid(row=1, column=0, padx=10, pady=10)
        self.cols_spinbox = Spinbox(config_window, from_=1, to=100, width=5)
        self.cols_spinbox.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Button(config_window, text="OK", command=lambda: self.set_configuration(config_window)).grid(row=2, column=0, columnspan=2, pady=10)
    
    def set_configuration(self, config_window):
        self.rows = int(self.rows_spinbox.get())
        self.cols = int(self.cols_spinbox.get())
        self.start_point = 1
        self.end_point = self.rows * self.cols
        populate_database(self.rows, self.cols, self.start_point, self.end_point)
        config_window.destroy()
        self.create_widgets()  # Create widgets after configuration is set
        self.create_menu()  # Create menu after configuration is set
    
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
        self.legend_canvas.create_text(40, 110, anchor="w", text="Out of Stock/Inaccessible", fill="black")
        
        self.path_output = tk.Text(self.root, height=5, width=50)
        self.path_output.grid(row=1, column=0, padx=10, pady=10)
        
        self.path_distance_label = tk.Label(control_frame, text="Total Path Distance: 0")
        self.path_distance_label.grid(row=4, column=0, padx=5, pady=5, columnspan=3)
        
        self.query_button = tk.Button(control_frame, text="Query ItemID", command=self.query_item_id)
        self.query_button.grid(row=5, column=0, padx=5, pady=5, columnspan=3)
        
        self.update_quantity_button = tk.Button(control_frame, text="Update Quantity", command=self.update_quantity)
        self.update_quantity_button.grid(row=6, column=0, padx=5, pady=5, columnspan=3)
    
        self.obstacle_mode = False
        self.obstacle_button = tk.Button(control_frame, text="Toggle Obstacle Mode", 
                                    command=self.toggle_obstacle_mode)
        self.obstacle_button.grid(row=7, column=0, padx=5, pady=5, columnspan=3)

        self.visualize_button = tk.Button(control_frame, 
                                    text="Open Grid Visualization",
                                    command=self.open_visualization_window)
        self.visualize_button.grid(row=8, column=0, padx=5, pady=5, columnspan=3)

    def toggle_obstacle_mode(self):
        self.obstacle_mode = not self.obstacle_mode
        if self.obstacle_mode:
            self.obstacle_button.config(relief="sunken", bg="gray")
        else:
            self.obstacle_button.config(relief="raised", bg="SystemButtonFace")

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

        How to Use:
        1. Configure the grid by entering the number of rows and columns.
        2. Enter the points you want to visit in the "Points" field.
        3. Click "Find Path" to calculate and visualize the shortest path.
        4. Use the "Query ItemID" button to get information about a specific item.
        5. Use the "Update Quantity" button to update the quantity of a specific item.
        6. Use the "Save Configuration" option to save the current grid configuration.
        7. Use the "Load Configuration" option to load a saved grid configuration.

        For more information, please refer to the user manual or contact support.

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
                cell_id = i * self.cols + j + 1
                
                # Set cell color based on status
                if is_obstacle(i, j):
                    fill_color = "gray"
                elif item and item[1] is not None and item[1] == 0:
                    fill_color = "red"
                else:
                    fill_color = "white"
                
                self.canvas.create_rectangle(x1, y1, x2, y2, 
                                        outline="black", 
                                        fill=fill_color,
                                        tags=f"cell_{cell_id}")
                
                if not is_obstacle(i, j):
                    # Draw cell number
                    self.canvas.create_text(x1 + cell_width/2, y1 + cell_height/2,
                                        text=str(cell_id),
                                        font=("Arial", font_size),
                                        fill="black",
                                        tags=f"text_{cell_id}")
                    

    def highlight_point(self, point, color):
        if self.canvas is None:
            return
            
        cell_width = min(800 // self.cols, 800 // self.rows)
        cell_height = cell_width
        row, col = divmod(point - 1, self.cols)
        x1 = col * cell_width
        y1 = row * cell_height
        
        # Create highlight while preserving existing cell color
        cell_tag = f"cell_{point}"
        text_tag = f"text_{point}"
        qty_tag = f"qty_{point}"
        
        # Add semi-transparent highlight
        highlight = self.canvas.create_rectangle(x1, y1, x1 + cell_width, y1 + cell_height,
                                            fill=color, stipple="gray50")
        
        # Raise existing elements above highlight
        self.canvas.tag_raise(cell_tag)
        self.canvas.tag_raise(text_tag)
        self.canvas.tag_raise(qty_tag)
        
    def on_canvas_click(self, event):
        cell_width = min(800 // self.cols, 800 // self.rows)
        cell_height = cell_width
        col = event.x // cell_width
        row = event.y // cell_height
        
        if self.obstacle_mode:
            current = is_obstacle(row, col)
            set_obstacle(row, col, not current)
            self.draw_grid()
        else:
            item = get_item(row, col)
            if item and item[1] is not None and not is_obstacle(row, col):
                self.show_item_info(row, col)
    
    def show_item_info(self, row, col):
        item = get_item(row, col)
        if item and item[1] is not None:  # Double check item exists and has quantity
            item_id = row * self.cols + col + 1
            messagebox.showinfo("Item Info", 
                f"ItemID: {item_id}\nRow: {row}\nCol: {col}\nQuantity: {item[1]}")
    
    def query_item_id(self):
        item_id = simpledialog.askinteger("Query ItemID", "Enter the ItemID:", minvalue=1)
        if item_id is not None:
            item = get_item_by_id(item_id)
            if item:
                row, col, quantity = item
                messagebox.showinfo("Item Info", f"ItemID: {item_id}\nRow: {row}\nCol: {col}\nQuantity: {quantity}")
            else:
                messagebox.showinfo("Item Info", "No item found.")
    
    # gui.py - Update update_quantity method
    def update_quantity(self):
        logger.debug("Starting quantity update")
        item_id = simpledialog.askinteger("Update Quantity", "Enter the ItemID:", minvalue=1)
        if item_id is not None:
            # Verify item exists
            item = get_item_by_id(item_id)
            logger.debug(f"ItemID entered: {item_id}")
            if not item:
                messagebox.showerror("Error", f"ItemID {item_id} does not exist")
                return
                
            quantity = simpledialog.askinteger("Update Quantity", 
                                            f"Enter the quantity for ItemID {item_id}:", 
                                            minvalue=0)
            logger.debug(f"Quantity entered: {quantity}")
            if quantity is not None:
                update_item_quantity(item_id, quantity)
                logger.info(f"Updated ItemID {item_id} quantity to {quantity}")
                messagebox.showinfo("Success", 
                                f"Updated quantity for ItemID {item_id} to {quantity}")
    
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
        logger.debug("Starting pathfinding calculation")
        try:
            points = list(map(int, self.points_entry.get().split(',')))
            self.points = points
            points_text = self.points_entry.get()
            logger.debug(f"Input points: {points_text}")

            if points_text.strip():
                points = [int(p.strip()) for p in points_text.split(',')]
                logger.debug(f"Parsed points: {points}")
            else:
                points = []
                logger.debug("No points provided")
                
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
            pathfinder = PathFinder(self.rows, self.cols)
            path = pathfinder.find_shortest_path(self.start_point, self.end_point, valid_points)
            if path:
                logger.info(f"Path found: {path}")
                self.path = path  # Store the path in an instance variable
                self.animate_path(path, valid_points)
                self.path_output.delete(1.0, tk.END)
                self.path_output.insert(tk.END, " -> ".join(map(str, path)))
                self.path_distance_label.config(text=f"Total Path Distance: {self.calculate_path_cost(path)}")
            else:
                messagebox.showinfo("No Path", "No path found between the given points.")
        except (ValueError, KeyError) as e:
            logger.error(f"Pathfinding failed: {str(e)}")
            messagebox.showerror("Path Error", str(e))
        
    def animate_path(self, path, valid_points):
        self.draw_grid()
        cell_width = min(800 // self.cols, 800 // self.rows)
        cell_height = cell_width
        
        # Track visited points to avoid multiple decrements
        visited_points = set()
        
        for i in range(len(path) - 1):
            current_point = path[i]
            next_point = path[i + 1]
            
            # Update quantity if point is in user-specified points
            if current_point in self.points and current_point not in visited_points:
                row, col = divmod(current_point - 1, self.cols)
                item = get_item(row, col)
                if item and item[1] is not None and item[1] > 0:
                    new_quantity = item[1] - 1
                    update_item_quantity(current_point, new_quantity)
                    logger.info(f"Updated quantity for point {current_point} to {new_quantity}")
                    visited_points.add(current_point)
            
            self.draw_arrow(current_point, next_point)
            self.root.update()
            self.root.after(100)
        
        # Check final point
        if path[-1] in self.points and path[-1] not in visited_points:
            row, col = divmod(path[-1] - 1, self.cols)
            item = get_item(row, col)
            if item and item[1] is not None and item[1] > 0:
                new_quantity = item[1] - 1
                update_item_quantity(path[-1], new_quantity)
                logger.info(f"Updated quantity for point {path[-1]} to {new_quantity}")
        
        # Redraw grid with updated quantities
        self.draw_grid()
        
        # Draw path visualization
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
                self.canvas.create_text(x1 + cell_width / 2, y1 + cell_height / 2, text=str(point), fill="black")
        
        # Highlight points
        self.highlight_point(self.start_point, "blue")
        self.highlight_point(self.end_point, "blue")
        
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