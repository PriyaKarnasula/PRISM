import re
import numpy as np
import pandas as pd
import customtkinter as ctk
from tkinter import messagebox
from tkinter import filedialog
import os
from PrismNestedTable import NestedTable  # Import your NestedTable class here
from PrismColumnTable import ColumnTable  # Import your ColumnTable class here
import copy

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

        self.prism_export_df = copy.deepcopy(self.parent.filtered_dfs)
        
        prism_type = self.parent.prism_export_dropdown.get()

        if prism_type == 'Nested':
            self.export_nested_table()
        elif prism_type == 'Columnar':
            self.export_columnar_table()
        
    def export_nested_table(self):
        input_prism_template = "templates/nested_template.pzfx"
        nested_dict = {}
        for group_name, df in self.prism_export_df:
            molecule_names = self.extract_molecule_names(df)
            for molecule in molecule_names:
                if molecule not in nested_dict:
                    nested_dict[molecule] = {}
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
        num_groups = len(self.prism_export_df)
        print(f"Number of groups: {num_groups}")
        template_folder = "templates"
        input_prism_template = os.path.join(template_folder, f"group{num_groups}.pzfx")

        molecule_dfs = {}
        all_group_dfs = {group_name: df for group_name, df in self.prism_export_df}
        print(f"Reformatting data for Prism: {all_group_dfs}")

        molecule_dfs = self.prepare_dict_for_columnar_export(all_group_dfs)

        # Specify the output file
        self.output_file = filedialog.asksaveasfilename(defaultextension=".pzfx", filetypes=[("Prism XML files", "*.pzfx")])

        if not self.output_file:
            return

        column_table = ColumnTable(molecule_dfs)
        column_table.to_xml(input_prism_template, self.output_file)
        return

    def extract_molecule_names(self,df):
        """Extract unique molecule names from DataFrame columns."""
        print(df)
        columns = df.columns
        molecule_names = set()
        for col in columns:
            match = re.match(r"(\D+)_m\d+", col)
            if match:
                molecule_names.add(match.group(1))
        print(f"Extracted molecule names: {molecule_names}")
        return list(molecule_names)
    
    def get_relavant_fields(self, table_name, lst_all_columns):
        table_name_related_columns = []

        for col in lst_all_columns:

            temp = col.split("####")[0].split('_')[:-1]
            if '_'.join(temp) == table_name:
                table_name_related_columns.append(col)
        return table_name_related_columns

    def prepare_dict_for_columnar_export(self, dict_df):

        # combining all the dataframes and added groupname to distinguish between the groups
        lst_df = []
        for group_name, group_df in dict_df.items():
            group_df.columns = [col + "####" + group_name for col in group_df.columns]
            group_df.reset_index(drop=True, inplace=True)
            lst_df.append(group_df)
        combined_df = pd.concat(lst_df, axis=1)

        # case pyruvicacid_something_m0####Group1 -> pyruvicacid_something_m0 ->  [pyruvicacid, soemthing, m0] -> [pyruvicacid, soemthing] -> pyruvicacid_soemthing
        # unique_tables are the molecule names
        unique_tables = list(set(['_'.join(col.split("####")[0].split('_')[:-1]) for col in combined_df.columns]))

        # creating a new dict datafarme 
        prism_dict = {}
        lst_all_columns = list(combined_df.columns)

        # sanity check
        if len(lst_all_columns) != len(set(lst_all_columns)):
            raise ValueError("Duplicate columns found, some issue with data, there might be duplicate group names")

        for table_name in unique_tables:
            prism_dict[table_name] = combined_df[self.get_relavant_fields(table_name, lst_all_columns)]

        # reformatting the field names
        for table_name, table_df in prism_dict.items():
            new_field_names = []
            for field in table_df.columns:
                group_name = field.split("####")[1]
                molecule_name = field.split("####")[0].split('_')[-1]
                new_field_names.append(f"{group_name}_{molecule_name}")

            # sorting to make sure the molucules are in order of m0, m1, m2
            table_df.columns = new_field_names
            new_field_names.sort(key = lambda x : x.split('_')[-1])
            table_df  = table_df[new_field_names]
            
            table_df = table_df.dropna(axis = 1, how = 'all')
            prism_dict[table_name] = table_df

        return prism_dict