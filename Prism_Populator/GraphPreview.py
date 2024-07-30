import pandas as pd
import customtkinter as ctk
from tkinter import messagebox
from tkinter import filedialog
from CriteriaApply import CriteriaApplication  # Import the new class
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PreviewGraph:
    def __init__(self, parent):
        self.parent = parent
        self.canvas = None  # To store the canvas of the graph

    def preview_graph(self):
        if not self.parent.selected_values_label:
            messagebox.showerror("Error", "Please select molecules before applying filters.")
            return
        if not hasattr(self.parent, 'group_frame') or not self.parent.group_frame:
            messagebox.showerror("Error", "No groups created yet. Please create groups first.")
            return
        if self.parent.graph_molecule_dropdown.get() == 'Select Molecule':
            messagebox.showerror("Error", "Please select a molecule to preview the graph.")
            return   
             
        selected_molecules = self.parent.selected_values_label.get("2.0", "end-1c").strip()
        selected_molecules = [m.strip() for m in selected_molecules.split("\n")  if m.strip()]

        selected_molecule = self.parent.graph_molecule_dropdown.get()
        
        valid_columns = [col for col in selected_molecules if col.startswith(selected_molecule)]

        if not valid_columns:
            messagebox.showerror("Error", f"No valid columns found for the selected molecule: {selected_molecule}")
            return
        
        # Subset the DataFrame to only include the valid columns
        filtered_dfs = {group_name: df[valid_columns] for group_name, df in self.parent.filtered_dfs}

        # Calculate mean values for each column in each group
        mean_values = {group_name: df.mean() for group_name, df in filtered_dfs.items()}

        # Prepare data for plotting
        plot_data = pd.DataFrame(mean_values)

        # Handling the existing graph
        if hasattr(self, 'canvas') and self.canvas:
            widget = self.canvas.get_tk_widget()
            if widget.winfo_exists():
                widget.destroy()
            self.canvas = None  # Clear the reference

        # Plotting the data
        fig, ax = plt.subplots()
        plot_data.plot(kind='bar', ax=ax)

        ax.set_xlabel('Molecules')
        ax.set_ylabel('Mean Values')
        ax.set_title(f'Graph Preview for {selected_molecule}')

        # Embed the plot in the Tkinter GUI
        self.canvas = FigureCanvasTkAgg(fig, master=self.parent.parent_group_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=self.parent.total_groups_created + 1, column=0, padx=10, pady=10)