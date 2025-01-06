import customtkinter as ctk
import pandas as pd
from tkinter import filedialog
import threading
from tkinter import messagebox
from CriteriaRow import CriteriaRow  
from CriteriaApply import CriteriaApplication  
from GraphPreview import PreviewGraph  
from PrismExport import ExportPrism 
from Group_Handling import GroupAndCriteria 
from MultiselectDropdownMolecules import DropDownMulitSelectMolecules
from MoveUpDown import MoveUpDown
import logging
import copy
import os
from File_operations import FileOperations

logger = logging.getLogger(__name__)

class Groups(ctk.CTkFrame):

    def __init__(self, master, nav_frame):
        super().__init__(master, )

        self.nav_frame = nav_frame

        self.nav_frame.columnconfigure(0, weight=1)
        self.nav_frame.columnconfigure(1, weight=1)
        self.nav_frame.columnconfigure(2, weight=1)
        self.nav_frame.columnconfigure(3, weight=1)
        self.nav_frame.columnconfigure(4, weight=1)

        self.nav_frame.rowconfigure(0, weight=1)
        self.nav_frame.rowconfigure(1, weight=15)
        self.nav_frame.rowconfigure(2, weight=1)
        self.nav_frame.rowconfigure(3, weight=1)

        self.molecule_names = []
        self.df = None
        self.criteria_rows = {}                      # Dictionary to store CriteriaRow instances by group ID or name
        self.file_operations = FileOperations(self)   # Initialize FileOperations instance
        self.group_and_criteria = GroupAndCriteria(self)  # Initialize GroupAndCriteria instance
        self.criteria_application = CriteriaApplication(self)
        self.previewing_graph = PreviewGraph(self)   # Initialize PreviewGraph instance
        self.export_to_prism = ExportPrism(self)     # Initialize ExportPrism instance
        self.selected_molecules = []
        self.unique_molecule_names = []
        self.filtered_dfs = {}                       # Initialize filtered_dfs 
        self.current_num_groups = 0                  # Initialize current_num_groups to 0

        self.file_frame = ctk.CTkFrame(nav_frame)
        self.file_frame.grid(row=0,column=0, padx=50, pady=0)
        open_file_btn = ctk.CTkButton(self.file_frame, text="Open Data File", command=self.file_operations.open_file)
        open_file_btn.grid(row=0,column=0)

        logger.info("Groups class initialized")

        self.molecule_frame = ctk.CTkFrame(nav_frame)
        self.molecule_frame.grid(row=0,column=2, padx=10)
        self.molecule_label = ctk.CTkLabel(self.molecule_frame,text="Molecules start from")
        self.molecule_label.grid(row=0,column=0,padx =10)
        self.molecule_dropdown = ctk.CTkComboBox(self.molecule_frame,values=self.molecule_names)
        self.molecule_dropdown.grid(row=0,column=1,sticky="w")
        self.molecule_dropdown.set('Select')           # Set default value

        self.group_number_frame = ctk.CTkFrame(nav_frame)
        self.group_number_frame.grid(row =0, column = 3, sticky='w', padx=10)
        self.group_number_label = ctk.CTkLabel(self.group_number_frame, text = 'Number of Groups')
        self.group_number_label.grid(row = 0, column = 0, padx =10, sticky='e')
        self.group_number_dropdown = ctk.CTkComboBox(self.group_number_frame, values = ['1','2','3','4', '5','6', '7', '8', '9', '10' ,'11', '12', '13', '14', '15'])
        self.group_number_dropdown.set('Select')
        self.group_number_dropdown.grid(row = 0, column =1, sticky = 'e')

        create_groups_btn = ctk.CTkButton(self.group_number_frame, text="Create Groups", command=lambda: self.group_and_criteria.create_groups(None))
        create_groups_btn.grid(row=0, column=4, padx=5, pady=5)

        self.compounds_frame = ctk.CTkFrame(nav_frame)
        self.compounds_frame.grid(row =0, column = 4, sticky='e', padx=10)
        self.compounds_label = ctk.CTkLabel(self.compounds_frame, text = 'Molecules')
        self.compounds_label.grid(row = 0, column = 0, padx =10, sticky='e')
        self.compound_select = ctk.CTkButton(self.compounds_frame, text="Click to Select", command=self.open_compounds_dropdown)
        self.compound_select.grid(row=0, column=1, padx=5, pady=5)
        self.selected_values_label = ctk.CTkTextbox(self.compounds_frame, width=200, height=50)
        self.selected_values_label.grid(row=1, column=1, padx=5, pady=5)

        self.parent_group_frame = ctk.CTkScrollableFrame(self.nav_frame)
        self.parent_group_frame.grid(row=1, column=0, columnspan=4, sticky="nsew")
        self.parent_group_frame.rowconfigure(0, weight =1)
        self.parent_group_frame.columnconfigure(0, weight =1)

        self.aggregate_groups_frame = ctk.CTkFrame(nav_frame)
        self.aggregate_groups_frame.grid(row=1, column=4, sticky="nsew", padx=5, pady=5)
        self.aggregate_groups_frame.columnconfigure(0, weight =1)
        self.aggregate_groups_frame.rowconfigure(0, weight =1)

        self.add_group_frame = ctk.CTkFrame(nav_frame)
        self.add_group_frame.grid(row=2, column=0, padx=5, pady=5)
        self.add_group_btn = ctk.CTkButton(self.add_group_frame, text="Add Group", command=self.group_and_criteria.add_group)
        self.add_group_btn.grid(row=0, column=0, padx=5, pady=5)

        self.apply_frame = ctk.CTkFrame(nav_frame)
        self.apply_frame.grid(row=3, column=0, padx=5, pady=5)
        self.apply_btn = ctk.CTkButton(self.apply_frame, text="Apply Filters", command=self.criteria_application.apply_criteria) #change command later
        self.apply_btn.grid(row=0, column=0, padx=5, pady=5)

        self.preview_graph_frame = ctk.CTkFrame(nav_frame)
        self.preview_graph_frame.grid(row=3, column=2, padx=0, pady=5)
        self.graph_molecule_dropdown = ctk.CTkComboBox(self.preview_graph_frame, values = self.unique_molecule_names)
        self.graph_molecule_dropdown.set('Select Molecule')
        self.graph_molecule_dropdown.grid(row = 0, column =0, padx=5, pady=5)        
        self.preview_graph_btn = ctk.CTkButton(self.preview_graph_frame, text="Preview Graph", command=self.previewing_graph.preview_graph) 
        self.preview_graph_btn.grid(row=0, column=1, padx=5, pady=5)

        self.prism_export_frame = ctk.CTkFrame(nav_frame)
        self.prism_export_frame.grid(row=3, column=3, padx=0, pady=5)
        self.prism_export_dropdown = ctk.CTkComboBox(self.prism_export_frame, values = ['Columnar','Nested']) 
        self.prism_export_dropdown.grid(row=0, column=0, padx=5, pady=5)
        self.prism_export_dropdown.set('Select')
        self.prism_export_btn = ctk.CTkButton(self.prism_export_frame, text="Export to PRISM", command=self.export_to_prism.prism_export) 
        self.prism_export_btn.grid(row=0, column=1, padx=5, pady=5)

        self.excel_export_frame = ctk.CTkFrame(nav_frame)
        self.excel_export_frame.grid(row=3, column=4, padx=0, pady=5)
        self.excel_export_btn = ctk.CTkButton(self.excel_export_frame, text="Export to Excel", command=self.export_to_excel) 
        self.excel_export_btn.grid(row=0, column=0, padx=5, pady=5)
   
    def update_molecule_dropdown(self):
        self.molecule_dropdown.configure(values=self.molecule_names)
        logger.info("Molecule dropdown updated")

    def open_compounds_dropdown(self):
        selected_molecule = self.molecule_dropdown.get()
        if selected_molecule == 'Select':
            messagebox.showerror("Error", "Please select a value for 'Molecules start from'.")
            return

        self.graph_molecule_dropdown.set('Select Molecule')

        # Index of the selected molecule
        start_index = self.df.columns.get_loc(selected_molecule)

        # Get all columns from the selected molecule to the end
        options = self.df.columns[start_index:].tolist()
        options = [str(item) for item in options]
        DropDownMulitSelectMolecules(self, self.compounds_frame, options, self.selected_values_label)

    def update_graph_molecule_dropdown(self, unique_molecule_names):
        self.unique_molecule_names = unique_molecule_names
        self.graph_molecule_dropdown.configure(values=self.unique_molecule_names)
        logger.info("Graph molecules dropdown updated")

    def export_to_excel(self):
        if not hasattr(self, 'filtered_dfs') or not self.filtered_dfs:
            messagebox.showerror("Error", "No data available. Please create the groups and apply the filters.")
            return
        if not hasattr(self, 'criteria_df') or self.criteria_df.empty:
            messagebox.showerror("Error", "Please apply the filters before exporting to excel.")
            return

        # Ask user for a save location
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                                                initialfile="Filtered_Data.xlsx")
        if not file_path:
            return                                # If user cancels, do nothing
        
        # Deep copy the criteria_df
        criteria_copy = copy.deepcopy(self.criteria_df)
        # Replace '=' with 'equals' in the criteria_copy(else, excel is writing = as 0)
        criteria_copy.replace("=", "equals", inplace=True)

        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            # Write criteria_df to the first sheet
            criteria_copy.to_excel(writer, sheet_name="Criteria", index=False)
            
            # Write each filtered DataFrame to subsequent sheets
            for group_name, df in self.filtered_dfs:
                df.to_excel(writer, sheet_name=group_name, index=False)

        logger.info(f"Excel file saved to {file_path}")

    