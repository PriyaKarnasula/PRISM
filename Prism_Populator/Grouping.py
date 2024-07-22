import customtkinter as ctk
import pandas as pd
from tkinter import filedialog
import threading
from tkinter import messagebox
from CriteriaRow import CriteriaRow  # Import the CriteriaRow class
from MultiselectDropdown import DropDownMulitSelect
import os

class Groups(ctk.CTkFrame):

    def __init__(self, master, nav_frame):
        super().__init__(master, )

        self.nav_frame = nav_frame

        self.nav_frame.columnconfigure(0, weight=1)
        self.nav_frame.columnconfigure(1, weight=1)
        self.nav_frame.columnconfigure(2, weight=1)
        self.nav_frame.columnconfigure(3, weight=1)
        self.nav_frame.columnconfigure(4, weight=1)
        self.nav_frame.columnconfigure(5, weight=1)
        self.nav_frame.columnconfigure(6, weight=1)

        self.nav_frame.rowconfigure(0, weight=1)
        self.nav_frame.rowconfigure(1, weight=1)
        self.nav_frame.rowconfigure(2, weight=1)
        self.nav_frame.rowconfigure(3, weight=1)

        self.molecule_names = []
        self.df = None
        self.criteria_rows = {}  # Dictionary to store CriteriaRow instances by group ID or name

        self.file_frame = ctk.CTkFrame(nav_frame)
        self.file_frame.grid(row=0,column=0, padx=50, pady=0)
        open_file_btn = ctk.CTkButton(self.file_frame, text="Open Data File", command=self.open_file)
        open_file_btn.grid(row=0,column=0)
        # self.filepath_label = ctk.CTkLabel(self.file_frame, text="No File Loaded")
        # self.filepath_label.grid(row=0,column=1,padx =10, sticky="w")


        self.molecule_frame = ctk.CTkFrame(nav_frame)
        self.molecule_frame.grid(row=0,column=2, padx=10)
        self.molecule_label = ctk.CTkLabel(self.molecule_frame,text="Molecules start from")
        self.molecule_label.grid(row=0,column=0,padx =10)
        self.molecule_dropdown = ctk.CTkComboBox(self.molecule_frame,values=self.molecule_names)
        self.molecule_dropdown.grid(row=0,column=1,sticky="w")
        self.molecule_dropdown.set('Select')  # Set default value

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
        self.compounds_frame.grid(row =0, column = 5, sticky='e', padx=10)
        self.compounds_label = ctk.CTkLabel(self.compounds_frame, text = 'Molecules')
        self.compounds_label.grid(row = 0, column = 0, padx =10, sticky='e')
        self.compound_select = ctk.CTkButton(self.compounds_frame, text="Click to Select", command=self.open_compounds_dropdown)
        self.compound_select.grid(row=0, column=1, padx=5, pady=5)
        self.selected_values_label = ctk.CTkTextbox(self.compounds_frame, width=200, height=50)
        self.selected_values_label.grid(row=1, column=1, padx=5, pady=5)

        self.parent_group_frame = ctk.CTkScrollableFrame(self.nav_frame, height = 650, width = 1490)
        self.parent_group_frame.grid(row=1, column=0, columnspan=6, sticky="nsew")
        self.parent_group_frame.rowconfigure(0, weight =1)
        self.parent_group_frame.columnconfigure(0, weight =1)

        self.add_group_frame = ctk.CTkFrame(nav_frame)
        self.add_group_frame.grid(row=2, column=0, padx=5, pady=5)
        self.add_group_btn = ctk.CTkButton(self.add_group_frame, text="Add Group", command=self.add_group)
        self.add_group_btn.grid(row=0, column=0, padx=5, pady=5)

        self.apply_frame = ctk.CTkFrame(nav_frame)
        self.apply_frame.grid(row=3, column=0, padx=5, pady=5)
        self.apply_btn = ctk.CTkButton(self.apply_frame, text="Apply Filters", command=self.apply_criteria) #change command later
        self.apply_btn.grid(row=0, column=0, padx=5, pady=5)

        self.csv_export_frame = ctk.CTkFrame(nav_frame)
        self.csv_export_frame.grid(row=3, column=1, padx=0, pady=5)
        self.csv_export_btn = ctk.CTkButton(self.csv_export_frame, text="Export to CSV", command=self.export_to_csv) #change command later
        self.csv_export_btn.grid(row=0, column=0, padx=5, pady=5)

        self.preview_prism_frame = ctk.CTkFrame(nav_frame)
        self.preview_prism_frame.grid(row=3, column=2, padx=0, pady=5)
        self.preview_prism_btn = ctk.CTkButton(self.preview_prism_frame, text="Preview PRISM", command=self.export_to_csv) #change command later
        self.preview_prism_btn.grid(row=0, column=0, padx=5, pady=5)
        self.prism_export_btn = ctk.CTkButton(self.preview_prism_frame, text="Export to PRISM", command=self.export_to_csv) #change command later
        self.prism_export_btn.grid(row=0, column=1, padx=5, pady=5)

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
            # print(self.df)
            self.molecule_names = self.df.columns[1:].tolist()
            self.is_roi = False
            self.update_molecule_dropdown()
            # filename = os.path.basename(filepath)
            # self.filepath_label.configure(text=filename)
        except Exception as e:
            print(f"Failed to load file: {e}")
        finally:
            self.remove_loading_label()

    def remove_loading_label(self):
        if hasattr(self, 'loading_label') and self.loading_label is not None:
            self.loading_label.destroy()
    
    def update_molecule_dropdown(self):
        self.molecule_dropdown.configure(values=self.molecule_names)

    def open_compounds_dropdown(self):
        selected_molecule = self.molecule_dropdown.get()
        if selected_molecule == 'Select':
            messagebox.showerror("Error", "Please select a value for 'Molecules start from'.")
            return

        # Find the index of the selected molecule
        start_index = self.df.columns.get_loc(selected_molecule)

        # Get all columns from the selected molecule to the end
        options_selected = self.df.columns[start_index:].tolist()
        options_selected = [str(item) for item in options_selected]
        DropDownMulitSelect(self.compounds_frame, options_selected, self.selected_values_label)

    def create_groups(self, event=None):

        # Validate if the data file is loaded
        if self.df is None:
            messagebox.showerror("Error", "Please open a data file first.")
            return

        # Validate if the "Molecules start from" value is selected
        if self.molecule_dropdown.get() == 'Select':
            messagebox.showerror("Error", "Please select a value for 'Molecules start from'.")
            return
        
        selected_value = self.group_number_dropdown.get()
        if selected_value.isdigit():  # Check if it's a valid number
            num_groups = int(selected_value)
            for widget in self.parent_group_frame.winfo_children():
                widget.destroy()

            self.group_frame = []
            self.total_groups_created = 0  # Reset total groups created
            for i in range(num_groups):
                group_container_frame = ctk.CTkFrame(self.parent_group_frame, border_width=2, corner_radius=10)
                group_container_frame.grid(row=i, column =0, padx=10, pady=5)
                group_container_frame.grid_columnconfigure(0, weight =1)
                group_container_frame.grid_rowconfigure(0, weight =1)
                group_container_frame.columnconfigure(0, weight =1)
                group_container_frame.rowconfigure(0, weight =1)
                group_container_frame.columnconfigure(1, weight =1)
                group_container_frame.rowconfigure(1, weight =1)
                self.group_frame.append(group_container_frame)
                self.create_group(i + 1, group_container_frame)
                self.total_groups_created += 1  # Increment the total groups created
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
        delete_group_btn = ctk.CTkButton(individual_group_number_frame, text="Delete Group", fg_color='transparent', border_width = 1, command=lambda gf=container_frame: self.delete_group(gf))
        delete_group_btn.grid(row=0, column=2, padx=5, pady=5)

        self.criteria_frame = ctk.CTkFrame(container_frame)
        self.criteria_frame.grid(row=1, column=0, padx=10, pady=5)
        self.add_criteria(group_number, self.criteria_frame,individual_group_name_entry)
        add_criteria_btn = ctk.CTkButton(container_frame, text="Add Criteria",fg_color='transparent', border_width = 1, command=lambda cf=self.criteria_frame: self.add_criteria(group_number, cf,individual_group_name_entry))
        add_criteria_btn.grid(row=2, column=0, padx=10, pady=5, sticky = 'w')

    def add_group(self):
        if not hasattr(self, 'group_frame') or not self.group_frame:
            messagebox.showerror("Error", "No groups created yet. Please create groups first.")
        else:
            new_group_number = self.total_groups_created + 1  # Increment the group number correctly
            self.total_groups_created += 1  # Update total groups created
            group_container_frame = ctk.CTkFrame(self.parent_group_frame, border_width=2, corner_radius=10)
            self.create_group(new_group_number, group_container_frame)
            group_container_frame.grid(row =new_group_number, column =0, padx = 10, pady = 10, sticky = 'w')
            self.group_frame.append(group_container_frame)
            self.update_group_dropdown()  # Update the dropdown when a new group is created

    def delete_group(self, group_frame):
        group_frame.destroy()
        self.group_frame.remove(group_frame)
        self.total_groups_created -=1
        self.update_group_dropdown()

    def update_group_dropdown(self):
        current_num_groups = self.total_groups_created 
        self.group_number_dropdown.set(str(current_num_groups))        

    def add_criteria(self, group_number, criteria_frame, individual_group_name_entry):
        criteria_row_instance = CriteriaRow(self, criteria_frame, self.molecule_names, self.df,individual_group_name_entry) 
        if group_number not in self.criteria_rows:
            self.criteria_rows[group_number] = []
        self.criteria_rows[group_number].append(criteria_row_instance)
        print(criteria_row_instance)

    def apply_criteria(self):
        group_data = []
        self.filtered_dfs = []
        for group_id, group_frame in enumerate(self.group_frame):
            print(group_id, group_frame)
            group_info = {"group_name": None, "criteria": []}

            # Find group name entry and criteria frames within the group frame
            for child in group_frame.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    for inner_child in child.winfo_children():
                        if isinstance(inner_child, ctk.CTkEntry):
                            group_info["group_name"] = inner_child.get()
                            print(group_info["group_name"])

            # Get criteria for the current group
            if group_id + 1 in self.criteria_rows:
                for criteria_row in self.criteria_rows[group_id + 1]:
                    selected_criteria = criteria_row.get_selected_criteria()
                    group_info["criteria"].append(selected_criteria)
                    print(f"Selected criteria for group {group_id + 1}: {selected_criteria}")

            group_data.append(group_info)

        for group in group_data:
            if not group["group_name"]:
                continue

            filtered_df = self.df.copy()
            for criteria in group["criteria"]:
                if criteria["criteria"] == "Equals":
                    filtered_df = filtered_df[filtered_df[criteria["column"]].isin(criteria["value"])]
                elif criteria["criteria"] == "Not Equal":
                    filtered_df = filtered_df[~filtered_df[criteria["column"]].isin(criteria["value"])]
                elif criteria["criteria"] == ">":
                    filtered_df = filtered_df[filtered_df[criteria["column"]] > float(criteria["value"])]
                elif criteria["criteria"] == "<":
                    filtered_df = filtered_df[filtered_df[criteria["column"]] < float(criteria["value"])]
                elif criteria["criteria"] == "=":
                    filtered_df = filtered_df[filtered_df[criteria["column"]] == float(criteria["value"])]
                elif criteria["criteria"] == "not =":
                    filtered_df = filtered_df[filtered_df[criteria["column"]] != float(criteria["value"])]

            self.filtered_dfs.append((group["group_name"], filtered_df))

        print("Filtered DataFrames created successfully.")
        print(self.filtered_dfs)

    def export_to_csv(self):
        if not hasattr(self, 'filtered_dfs') or not self.filtered_dfs:
            messagebox.showerror("Error", "No data available. Please create the groups and apply the filters.")
            return

        for group_name, df in self.filtered_dfs:
            filename = f"{group_name}.csv"
            df.to_csv(filename, index=False)
            print(f"Data for group {group_name} exported to {filename}.")

        print("All filtered data exported successfully.")

    def get_criteria(self):
        # Call the getter method to get the selected value from the combo box
        selected_criteria = self.criteria_row_instance.get_selected_criteria()
        print(f"Selected criteria: {selected_criteria}")    

    