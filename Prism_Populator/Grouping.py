import customtkinter as ctk
import pandas as pd
from tkinter import filedialog
import threading
from tkinter import messagebox
from CriteriaRow import CriteriaRow  
from CriteriaApply import CriteriaApplication  
from GraphPreview import PreviewGraph  
from PrismExport import ExportPrism  
from MultiselectDropdownMolecules import DropDownMulitSelectMolecules
from MoveUpDown import MoveUpDown
import logging
import copy
import os

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
        self.criteria_application = CriteriaApplication(self)
        self.previewing_graph = PreviewGraph(self)   # Initialize PreviewGraph instance
        self.export_to_prism = ExportPrism(self)     # Initialize ExportPrism instance
        self.selected_molecules = []
        self.unique_molecule_names = []
        self.filtered_dfs = {}                       # Initialize filtered_dfs 
        self.current_num_groups = 0                  # Initialize current_num_groups to 0

        self.file_frame = ctk.CTkFrame(nav_frame)
        self.file_frame.grid(row=0,column=0, padx=50, pady=0)
        open_file_btn = ctk.CTkButton(self.file_frame, text="Open Data File", command=self.open_file)
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

        create_groups_btn = ctk.CTkButton(self.group_number_frame, text="Create Groups", command=lambda: self.create_groups(None))
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
        self.add_group_btn = ctk.CTkButton(self.add_group_frame, text="Add Group", command=self.add_group)
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

        self.loading_label = ctk.CTkLabel(self.nav_frame, text="Loading...")
        self.loading_label.grid(row=0, column=1, padx=0, pady=0)

    def load_file(self, filepath):
        try:
            self.df = pd.read_csv(filepath, index_col=False, low_memory=False)
            self.molecule_names = self.df.columns[1:].tolist()
            self.is_roi = False
            logger.info("Data file loaded successfully")
            self.update_molecule_dropdown()
        except Exception as e:
            print(f"Failed to load file: {e}")
        finally:
            self.remove_loading_label()

    def remove_loading_label(self):
        if hasattr(self, 'loading_label') and self.loading_label is not None:
            self.loading_label.destroy()
    
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

    def create_groups(self, event=None):
        # Validate if the data file is loaded
        if self.df is None:
            messagebox.showerror("Error", "Please open a data file first.")
            return

        # Validate if the "Molecules start from" value is selected
        if self.molecule_dropdown.get() == 'Select':
            messagebox.showerror("Error", "Please select a value for 'Molecules start from'.")
            return
        
        # Destroy existing groups
        for child in self.parent_group_frame.winfo_children():
            child.destroy()
        self.criteria_rows.clear() 

        selected_value = self.group_number_dropdown.get()
        if selected_value.isdigit():                      # Check if it's a valid number
            num_groups = int(selected_value)

            self.group_frame = []
            self.total_groups_created = 0                 # Reset total groups created

            for i in range(num_groups):
                group_container_frame = ctk.CTkFrame(self.parent_group_frame,  border_width=2, corner_radius=10)
                group_container_frame.grid(row=i, column =0, padx=10, pady=5)
                group_container_frame.grid_columnconfigure(0, weight =1)
                group_container_frame.grid_rowconfigure(0, weight =1)
                group_container_frame.columnconfigure(0, weight =1)
                group_container_frame.rowconfigure(0, weight =1)
                group_container_frame.columnconfigure(1, weight =1)
                group_container_frame.rowconfigure(1, weight =1)
                self.group_frame.append(group_container_frame)
                self.create_group(i + 1, group_container_frame)
                self.total_groups_created += 1            # Increment the total groups created
        else:
            # Handles the case where 'Select' or an invalid string is selected
            pass

    def create_group(self, group_number, container_frame):
    
        individual_group_number_frame = ctk.CTkFrame(container_frame)
        individual_group_number_frame.grid(row =0, column = 0, padx = 10, pady = 5, sticky = 'w')
        individual_group_number_frame.columnconfigure(0, weight=1)
        individual_group_number_label = ctk.CTkLabel(individual_group_number_frame, text=f"Group {group_number} Name:")
        individual_group_number_label.grid(row = 0, column = 0, padx = 10, pady = 5, sticky = 'w')
        individual_group_name_entry = ctk.CTkEntry(individual_group_number_frame)
        individual_group_name_entry.grid(row=0, column=1, padx = 20, pady = 5)
        delete_group_btn = ctk.CTkButton(individual_group_number_frame, text="Delete Group", fg_color='transparent', border_width = 1, command=lambda gf=container_frame, gn=group_number : self.delete_group(gf, gn))
        delete_group_btn.grid(row=0, column=2, padx=5, pady=5)

        self.criteria_frame = ctk.CTkFrame(container_frame)
        self.criteria_frame.grid(row=1, column=0, padx=10, pady=5)
        self.add_criteria(group_number, self.criteria_frame,individual_group_name_entry)
        add_criteria_btn = ctk.CTkButton(container_frame, text="Add Criteria",fg_color='transparent', border_width = 1, command=lambda cf=self.criteria_frame: self.add_criteria(group_number, cf,individual_group_name_entry))
        add_criteria_btn.grid(row=2, column=0, padx=10, pady=5, sticky = 'w')

        logger.info(f"Group {group_number} created")

    def add_group(self):
        if not hasattr(self, 'group_frame') or not self.group_frame:
            messagebox.showerror("Error", "No groups created yet. Please create groups first.")
            return
        if self.total_groups_created == 15:
            messagebox.showerror("Error", "Maximum number of groups reached.")
            return
        # Find the maximum existing group number
        existing_group_numbers = [key for key in self.criteria_rows.keys()]
        if existing_group_numbers:
            new_group_number = max(existing_group_numbers) + 1
        else:
            new_group_number = 1

        # Handling the existing graph
        if hasattr(self.previewing_graph, 'canvas') and self.previewing_graph.canvas:
            widget = self.previewing_graph.canvas.get_tk_widget()
            if widget.winfo_exists():
                widget.destroy()
            self.previewing_graph.canvas = None           # Clear the reference

        for child in self.aggregate_groups_frame.winfo_children():
            child.destroy()

        self.total_groups_created += 1                    # Update total groups created
        group_container_frame = ctk.CTkFrame(self.parent_group_frame, border_width=2, corner_radius=10)
        self.create_group(new_group_number, group_container_frame)
        group_container_frame.grid(row =self.total_groups_created, column =0, padx = 10, pady = 5)
        group_container_frame.grid_columnconfigure(0, weight =1)
        group_container_frame.grid_rowconfigure(0, weight =1)
        group_container_frame.columnconfigure(0, weight =1)
        group_container_frame.rowconfigure(0, weight =1)
        group_container_frame.columnconfigure(1, weight =1)
        group_container_frame.rowconfigure(1, weight =1)
        self.group_frame.append(group_container_frame)
        self.update_group_dropdown()                      # Update the dropdown when a new group is created

    def delete_group(self, group_frame, group_number):
        # Handling the existing graph
        if hasattr(self.previewing_graph, 'canvas') and self.previewing_graph.canvas:
            widget = self.previewing_graph.canvas.get_tk_widget()
            if widget.winfo_exists():
                widget.destroy()
            self.previewing_graph.canvas = None            # Clear the reference

        for child in self.aggregate_groups_frame.winfo_children():
            child.destroy()

        group_frame.destroy()
        self.group_frame.remove(group_frame)
        # Remove criteria for the deleted group
        if group_number in self.criteria_rows:
            del self.criteria_rows[group_number]

        # Re-arrange the remaining groups
        for i, frame in enumerate(self.group_frame):
            frame.grid(row=i, column=0, padx=10, pady=5)

        self.total_groups_created -=1
        self.update_group_dropdown()

        logger.info(f"Group {group_number} deleted")

    def update_group_dropdown(self):
        self.current_num_groups = self.total_groups_created 
        self.group_number_dropdown.set(str(self.current_num_groups))    
        
        logger.info("Number of Groups dropdown updated based on groups added/deleted")    

    def add_criteria(self, group_number, criteria_frame, individual_group_name_entry):
        # Handling the existing graph
        if hasattr(self.previewing_graph, 'canvas') and self.previewing_graph.canvas:
            widget = self.previewing_graph.canvas.get_tk_widget()
            if widget.winfo_exists():
                widget.destroy()
            self.previewing_graph.canvas = None  
        
        for child in self.aggregate_groups_frame.winfo_children():
            child.destroy()

        criteria_row_instance = CriteriaRow(self, criteria_frame, self.molecule_names, self.df,individual_group_name_entry,  parent_class=self) 
        if group_number not in self.criteria_rows:
            self.criteria_rows[group_number] = []
        self.criteria_rows[group_number].append(criteria_row_instance)
        # print(criteria_row_instance)
        logger.info(f"Criteria added for group {group_number}")

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

        # print(f"Excel file saved to {file_path}")
        logger.info(f"Excel file saved to {file_path}")

    def get_criteria(self):
        # Call the method to get the selected value from the combo box
        selected_criteria = self.criteria_row_instance.get_selected_criteria()
        # print(f"Selected criteria: {selected_criteria}")    

    