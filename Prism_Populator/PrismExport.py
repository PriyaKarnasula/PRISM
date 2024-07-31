import re
import pandas as pd
import customtkinter as ctk
from tkinter import messagebox
from tkinter import filedialog
import os
from PrismNestedTable import NestedTable  # Import your NestedTable class here

class ExportPrism:
    def __init__(self, parent):
        self.parent = parent

    def prism_export(self):
        if not hasattr(self.parent, 'group_frame') or not self.parent.group_frame:
            messagebox.showerror("Error", "No groups created yet. Please create groups first.")
            return
        
        if not self.parent.filtered_dfs:
            messagebox.showerror("Error", "No data to export. Please apply filters first.")
            return
        
        print(self.parent.filtered_dfs)
        
        prism_type = self.parent.prism_export_dropdown.get()

        if prism_type == 'Nested':
            output = self.export_nested_table()
        elif prism_type == 'Columnar':
            output = self.export_columnar_table()
        
    def export_nested_table(self):
        input_prism_template = "templates/nested_template.pzfx"
        nested_dict = {}
        for idx, (group_name, df) in enumerate(self.parent.filtered_dfs):
            molecule_names = self.extract_molecule_names(df)
            for molecule in molecule_names:
                if molecule not in nested_dict:
                    nested_dict[molecule] = {}
                # group_label = group_name[idx] if idx < len(group_name) else f"Group_{idx+1}"
                group_label = group_name
                nested_dict[molecule][group_label] = df.filter(regex=f"^{molecule}_m")

        print(nested_dict)

        # Specify the output file
        self.output_file = filedialog.asksaveasfilename(defaultextension=".pzfx", filetypes=[("Prism XML files", "*.pzfx")])
        
        if not self.output_file:
            return

        nested_table = NestedTable(nested_dict)
        nested_table.to_xml(input_prism_template, self.output_file)
        return
    
    def export_columnar_table(self):
        # Automatically pick the correct template based on the number of groups
        num_groups = len(self.parent.filtered_dfs)
        print(f"Number of groups: {num_groups}")
        template_folder = "templates"
        input_prism_template = os.path.join(template_folder, f"group{num_groups}.pzfx") 

    def extract_molecule_names(self,df):
        """Extract unique molecule names from DataFrame columns."""
        columns = df.columns
        molecule_names = set()
        for col in columns:
            match = re.match(r"(\D+)_m\d+", col)
            if match:
                molecule_names.add(match.group(1))
        print(f"Extracted molecule names: {molecule_names}")
        return list(molecule_names)