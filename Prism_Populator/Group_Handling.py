import pandas as pd
import customtkinter as ctk
from tkinter import messagebox
import logging
from CriteriaRow import CriteriaRow  

logger = logging.getLogger(__name__)

class GroupAndCriteria:
    def __init__(self, parent):
        self.parent = parent

    def create_groups(self, event=None):
        # Validate if the data file is loaded
        if self.parent.df is None:
            messagebox.showerror("Error", "Please open a data file first.")
            return

        # Validate if the "Molecules start from" value is selected
        if self.parent.molecule_dropdown.get() == 'Select':
            messagebox.showerror("Error", "Please select a value for 'Molecules start from'.")
            return
        
        # Destroy existing groups
        for child in self.parent.parent_group_frame.winfo_children():
            child.destroy()
        self.parent.criteria_rows.clear() 
        self.delete_group_buttons = []  # Keep track of all delete group buttons

        selected_value = self.parent.group_number_dropdown.get()
        if selected_value.isdigit():                      # Check if it's a valid number
            num_groups = int(selected_value)

            self.parent.group_frame = []
            self.parent.total_groups_created = 0                 # Reset total groups created

            for i in range(num_groups):
                group_container_frame = ctk.CTkFrame(self.parent.parent_group_frame,  border_width=2, corner_radius=10)
                group_container_frame.grid(row=i, column =0, padx=10, pady=5)
                group_container_frame.grid_columnconfigure(0, weight =1)
                group_container_frame.grid_rowconfigure(0, weight =1)
                group_container_frame.columnconfigure(0, weight =1)
                group_container_frame.rowconfigure(0, weight =1)
                group_container_frame.columnconfigure(1, weight =1)
                group_container_frame.rowconfigure(1, weight =1)
                self.parent.group_frame.append(group_container_frame)
                # logger.info(self.parent.group_frame)
                self.create_group(i + 1, group_container_frame)
                self.parent.total_groups_created += 1            # Increment the total groups created
            # self.update_delete_buttons_state()  # Update delete buttons' state
        else:
            # Handles the case where 'Select' or an invalid string is selected
            pass

    def create_group(self, group_number, container_frame):
        # self.parent.filtered_df[group_number] = self.parent.df

        individual_group_number_frame = ctk.CTkFrame(container_frame)
        individual_group_number_frame.grid(row =0, column = 0, padx = 10, pady = 5, sticky = 'w')
        individual_group_number_frame.columnconfigure(0, weight=1)
        individual_group_number_label = ctk.CTkLabel(individual_group_number_frame, text=f"Group {group_number} Name:")
        individual_group_number_label.grid(row = 0, column = 0, padx = 10, pady = 5, sticky = 'w')
        individual_group_name_entry = ctk.CTkEntry(individual_group_number_frame)
        individual_group_name_entry.grid(row=0, column=1, padx = 20, pady = 5)
        delete_group_btn = ctk.CTkButton(individual_group_number_frame, text="Delete Group", fg_color='transparent', border_width = 1, command=lambda gf=container_frame, gn=group_number : self.delete_group(gf, gn))
        delete_group_btn.grid(row=0, column=2, padx=5, pady=5)
        self.delete_group_buttons.append(delete_group_btn)  # Track this button for enabling/disabling later

        self.criteria_frame = ctk.CTkFrame(container_frame)
        self.criteria_frame.grid(row=1, column=0, padx=10, pady=5)
        self.add_criteria(group_number, self.criteria_frame,individual_group_name_entry)
        add_criteria_btn = ctk.CTkButton(container_frame, text="Add Criteria",fg_color='transparent', border_width = 1, command=lambda cf=self.criteria_frame: self.add_criteria(group_number, cf,individual_group_name_entry))
        add_criteria_btn.grid(row=2, column=0, padx=10, pady=5, sticky = 'w')

        # self.update_delete_buttons_state()

        logger.info(f"Group {group_number} created")
    
    def update_delete_buttons_state(self):
        # Disable delete buttons for all groups except the last one
        for i, frame in enumerate(self.parent.group_frame):
            delete_group_btn = frame.winfo_children()[0].winfo_children()[2]
            if i == self.parent.total_groups_created - 1:
                delete_group_btn.configure(state='normal')
            else:
                delete_group_btn.configure(state='disabled')

    def add_group(self):
        if not self.parent.group_frame:
            messagebox.showerror("Error", "No groups created yet. Please create groups first.")
            return
        if self.parent.total_groups_created == 15:
            messagebox.showerror("Error", "Maximum number of groups reached.")
            return
        # Find the maximum existing group number
        existing_group_numbers = [key for key in self.parent.criteria_rows.keys()]
        if existing_group_numbers:
            new_group_number = max(existing_group_numbers) + 1
        else:
            new_group_number = 1

        # Handling the existing graph
        if hasattr(self.parent.previewing_graph, 'canvas') and self.parent.previewing_graph.canvas:
            widget = self.parent.previewing_graph.canvas.get_tk_widget()
            if widget.winfo_exists():
                widget.destroy()
            self.parent.previewing_graph.canvas = None           # Clear the reference

        for child in self.parent.aggregate_groups_frame.winfo_children():
            child.destroy()

        self.parent.total_groups_created += 1                    # Update total groups created
        group_container_frame = ctk.CTkFrame(self.parent.parent_group_frame, border_width=2, corner_radius=10)
        self.create_group(new_group_number, group_container_frame)
        group_container_frame.grid(row =self.parent.total_groups_created, column =0, padx = 10, pady = 5)
        group_container_frame.grid_columnconfigure(0, weight =1)
        group_container_frame.grid_rowconfigure(0, weight =1)
        group_container_frame.columnconfigure(0, weight =1)
        group_container_frame.rowconfigure(0, weight =1)
        group_container_frame.columnconfigure(1, weight =1)
        group_container_frame.rowconfigure(1, weight =1)
        self.parent.group_frame.append(group_container_frame)
        self.update_group_dropdown()                      # Update the dropdown when a new group is created

    def delete_group(self, group_frame, group_number):
        # Handling the existing graph
        if hasattr(self.parent.previewing_graph, 'canvas') and self.parent.previewing_graph.canvas:
            widget = self.parent.previewing_graph.canvas.get_tk_widget()
            if widget.winfo_exists():
                widget.destroy()
            self.parent.previewing_graph.canvas = None            # Clear the reference

        for child in self.parent.aggregate_groups_frame.winfo_children():
            child.destroy()

        group_frame.destroy()
        self.parent.group_frame.remove(group_frame)

        # Remove the last delete button from the list
        self.delete_group_buttons.pop()  
        # Remove criteria for the deleted group
        if group_number in self.parent.criteria_rows:
            del self.parent.criteria_rows[group_number]

        # Re-arrange the remaining groups
        for i, frame in enumerate(self.parent.group_frame):
            frame.grid(row=i, column=0, padx=10, pady=5)

        self.parent.total_groups_created -=1
        self.update_group_dropdown()
        # self.update_delete_buttons_state()

        logger.info(f"Group {group_number} deleted")

    def update_group_dropdown(self):
        self.current_num_groups = self.parent.total_groups_created 
        self.parent.group_number_dropdown.set(str(self.current_num_groups))    
        
        logger.info("Number of Groups dropdown updated based on groups added/deleted")    

    def add_criteria(self, group_number, criteria_frame, individual_group_name_entry):
        # Handling the existing graph
        if hasattr(self.parent.previewing_graph, 'canvas') and self.parent.previewing_graph.canvas:
            widget = self.parent.previewing_graph.canvas.get_tk_widget()
            if widget.winfo_exists():
                widget.destroy()
            self.parent.previewing_graph.canvas = None  
        
        for child in self.parent.aggregate_groups_frame.winfo_children():
            child.destroy()

        criteria_row_instance = CriteriaRow(self.parent, criteria_frame, self.parent.molecule_names, self.parent.df,individual_group_name_entry,  parent_class=self.parent) 
        if group_number not in self.parent.criteria_rows:
            self.parent.criteria_rows[group_number] = []
        self.parent.criteria_rows[group_number].append(criteria_row_instance)
        # print(criteria_row_instance)
        logger.info(f"Criteria added for group {group_number}")

        # for group_number, rows in self.parent.criteria_rows.items():
        #     for i, row in enumerate(rows):
        #         if i != len(rows) - 1:
        #             row.disable()  # Enable the last row
        #         else:
        #             return  # Disable all other rows

