import tkinter as tk
from tkinter import Toplevel, Spinbox
from database import populate_database

class ConfigScreen:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        self.show_configuration_screen()

    def show_configuration_screen(self):
        self.config_window = Toplevel(self.root)
        self.config_window.title("Configure Grid")
        
        tk.Label(self.config_window, text="Rows:").grid(row=0, column=0, padx=10, pady=10)
        self.rows_spinbox = Spinbox(self.config_window, from_=1, to=100, width=5)
        self.rows_spinbox.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(self.config_window, text="Columns:").grid(row=1, column=0, padx=10, pady=10)
        self.cols_spinbox = Spinbox(self.config_window, from_=1, to=100, width=5)
        self.cols_spinbox.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Button(self.config_window, text="OK", command=self.set_configuration).grid(row=2, column=0, columnspan=2, pady=10)
    
    def set_configuration(self):
        rows = int(self.rows_spinbox.get())
        cols = int(self.cols_spinbox.get())
        start_point = 1
        end_point = rows * cols
        populate_database(rows, cols, start_point, end_point)
        self.callback(rows, cols, start_point, end_point)
        self.config_window.destroy()