import customtkinter as ctk
import pandas as pd
from tkinter import filedialog
import threading
from tkinter import messagebox
from CriteriaRow import CriteriaRow  # Import the CriteriaRow class

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

        self.molecule_names = []
        self.df = None

        open_file_btn = ctk.CTkButton(nav_frame, text="Open Data File", command=self.open_file)
        open_file_btn.grid(row=0,column=0,padx =50,pady = 15, sticky="e")


        self.molecule_frame = ctk.CTkFrame(nav_frame)
        self.molecule_frame.grid(row=0,column=2,sticky="e", padx=50)
        self.molecule_label = ctk.CTkLabel(self.molecule_frame,text="Molecules start from")
        self.molecule_label.grid(row=0,column=0,padx =10, sticky="e")
        self.molecule_dropdown = ctk.CTkComboBox(self.molecule_frame,values=self.molecule_names)
        self.molecule_dropdown.grid(row=0,column=1,sticky="e")
        self.molecule_dropdown.set('Select')  # Set default value

        self.group_number_frame = ctk.CTkFrame(nav_frame)
        self.group_number_frame.grid(row =0, column = 4, sticky='e', padx=50)
        self.group_number_label = ctk.CTkLabel(self.group_number_frame, text = 'Number of Groups')
        self.group_number_label.grid(row = 0, column = 0, padx =10, sticky='e')
        self.group_number_dropdown = ctk.CTkComboBox(self.group_number_frame, values = ['1','2','3','4', '5','6', '7', '8', '9', '10' ,'11', '12', '13', '14', '15'])
        self.group_number_dropdown.set('Select')
        self.group_number_dropdown.grid(row = 0, column =1, sticky = 'e')

        create_groups_btn = ctk.CTkButton(self.group_number_frame, text="Create Groups", command=lambda: self.create_groups(None))
        create_groups_btn.grid(row=0, column=5, padx=5, pady=5)

        self.parent_group_frame = ctk.CTkScrollableFrame(self.nav_frame, height = 700, width = 1490)
        self.parent_group_frame.grid(row=1, column=0, columnspan=6, sticky="nsew")

        self.add_group_frame = ctk.CTkFrame(nav_frame)
        self.add_group_frame.grid(row=2, column=0, padx=5, pady=5)
        self.add_group_btn = ctk.CTkButton(self.add_group_frame, text="Add Group", command=self.add_group)
        self.add_group_btn.grid(row=0, column=0, padx=5, pady=5)

        self.apply_frame = ctk.CTkFrame(nav_frame)
        self.apply_frame.grid(row=3, column=0, padx=5, pady=5)
        self.apply_btn = ctk.CTkButton(self.apply_frame, text="Apply", command=self.apply_criteria) #change command later
        self.apply_btn.grid(row=0, column=0, padx=5, pady=5)
        self.csv_export_btn = ctk.CTkButton(self.apply_frame, text="Export Group data to CSV", command=self.export_to_csv) #change command later
        self.csv_export_btn.grid(row=0, column=1, padx=5, pady=5)

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
        self.loading_label.grid(row=0, column=2, padx=(5, 0), pady=(10, 10), sticky="w")

    def load_file(self, filepath):
        try:
            self.df = pd.read_csv(filepath, index_col=False, low_memory=False)
            # print(self.df)
            self.molecule_names = self.df.columns[1:].tolist()
            self.is_roi = False
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

    def create_groups(self, event=None):

        # # Validate if the data file is loaded
        # if self.df is None:
        #     messagebox.showerror("Error", "Please open a data file first.")
        #     return

        # # Validate if the "Molecules start from" value is selected
        # if self.molecule_dropdown.get() == 'Select':
        #     messagebox.showerror("Error", "Please select a value for 'Molecules start from'.")
        #     return
        
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
                group_container_frame.columnconfigure(0, weight =1)
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

        criteria_frame = ctk.CTkFrame(container_frame)
        criteria_frame.grid(row=1, column=0, padx=10, pady=5)
        self.add_criteria(criteria_frame)
        add_criteria_btn = ctk.CTkButton(container_frame, text="Add Criteria",fg_color='transparent', border_width = 1, command=lambda cf=criteria_frame: self.add_criteria(cf))
        add_criteria_btn.grid(row=2, column=0, padx=10, pady=5, sticky = 'w')

        self.group_frame.append(individual_group_number_frame)

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

    def add_criteria(self, criteria_frame):
        CriteriaRow(self, criteria_frame, self.molecule_names, self.df) 

    def apply_criteria(self):
        groups_data = []
        
        for group_container in self.parent_group_frame.winfo_children():
            criteria_rows = group_container.winfo_children()[1].winfo_children()
            # print(criteria_rows)
            group_df = self.df.copy()
            
            for i in range(0, len(criteria_rows), 9):
                column = criteria_rows[i + 1].cget("text") if isinstance(criteria_rows[i + 1], ctk.CTkLabel) else criteria_rows[i + 1].get()
                criteria = criteria_rows[i + 3].cget("text") if isinstance(criteria_rows[i + 3], ctk.CTkLabel) else criteria_rows[i + 3].get()
                value = criteria_rows[i + 5].cget("text") if isinstance(criteria_rows[i + 5], ctk.CTkLabel) else criteria_rows[i + 5].get()
                data_rows_label = criteria_rows[i + 7]  # Reference to the data rows label
            
                
                if column and criteria and value:
                    if criteria in [">", "<", "=", "not ="]:
                        value = float(value) if pd.api.types.is_numeric_dtype(group_df[column]) else value
                        if criteria == ">":
                            group_df = group_df[group_df[column] > value]
                        elif criteria == "<":
                            group_df = group_df[group_df[column] < value]
                        elif criteria == "=":
                            group_df = group_df[group_df[column] == value]
                        elif criteria == "not =":
                            group_df = group_df[group_df[column] != value]
                    else:
                        if criteria == "single selection":
                            group_df = group_df[group_df[column] == value]
                        elif criteria == "multiple selection":
                            values = value.split(",")
                            group_df = group_df[group_df[column].isin(values)]
                        elif criteria == "not equal":
                            group_df = group_df[group_df[column] != value]
                
                data_rows_label.configure(text=str(len(group_df)))  # Update the number of rows label
                
            groups_data.append(group_df)
        
        self.groups_data = groups_data
        print(self.groups_data)

    def export_to_csv(self):
        for idx, group_data in enumerate(self.groups_data):
            filepath = filedialog.asksaveasfilename(defaultextension=".csv", title=f"Save Group {idx + 1} Data", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
            if filepath:
                group_data.to_csv(filepath, index=False)
                messagebox.showinfo("Info", f"Group {idx + 1} data exported to {filepath}")
