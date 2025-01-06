import customtkinter as ctk
import pandas as pd
from tkinter import filedialog
import threading 
import logging
import os

logger = logging.getLogger(__name__)

class FileOperations:
    def __init__(self, parent):
        self.parent = parent

    def open_file(self):
            self.filepath = filedialog.askopenfilename(
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            if self.filepath:
                print(self.filepath)
                self.display_file_loading()
                threading.Thread(target=self.load_file, args=(self.filepath,), daemon=True).start()

    def display_file_loading(self):
        # Destroy previous loading label if it exists
        if hasattr(self, 'loading_label') and self.loading_label is not None:
            self.loading_label.destroy()

        self.loading_label = ctk.CTkLabel(self.parent.nav_frame, text="Loading...")
        self.loading_label.grid(row=0, column=1, padx=0, pady=0)

    def load_file(self, filepath):
        try:
            self.parent.df = pd.read_csv(filepath, index_col=False, low_memory=False)
            self.parent.molecule_names = self.parent.df.columns[1:].tolist()
            self.is_roi = False
            logger.info("Data file loaded successfully")
            self.parent.update_molecule_dropdown()

            # Extract the file name for display
            self.file_name = os.path.basename(filepath)

        except Exception as e:
            print(f"Failed to load file: {e}")
        finally:
            self.remove_loading_label()

    def remove_loading_label(self):
        if hasattr(self, 'loading_label') and self.loading_label is not None:
            self.loading_label.destroy()
        if self.file_name:
            # Display the first 10 characters of the file name followed by "..."
            truncated_name = (self.file_name[:10] + '...') if len(self.file_name) > 10 else self.file_name
            self.loading_label = ctk.CTkLabel(self.parent.nav_frame, text=f"{truncated_name}")
            self.loading_label.grid(row=0, column=1, padx=0, pady=0)
