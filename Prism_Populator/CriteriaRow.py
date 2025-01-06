import customtkinter as ctk
import pandas as pd
from MultiselectDropdown import DropDownMulitSelect
from tkinter import messagebox
from GraphPreview import PreviewGraph  # Import the new class
import logging

logger = logging.getLogger(__name__)

class CriteriaRow(ctk.CTkFrame):
    def __init__(self, master, parent_frame, molecule_names, df,group_name_entry, parent_class):
        super().__init__(master, )

        self.parent_frame = parent_frame
        self.molecule_names = molecule_names
        self.df = df
        self.group_name_entry = group_name_entry
        self.parent_class = parent_class
        self.previewing_graph = PreviewGraph(self.master)   # Initialize PreviewGraph instance

        self.add_criteria_row()

    def add_criteria_row(self):
        self.row_idx = len(self.parent_frame.winfo_children())
        # print(self.row_idx)
        self.column_label = ctk.CTkLabel(self.parent_frame, text='Grouping Column')
        self.column_label.grid(row=self.row_idx, column=0, padx=10, sticky='e')
        self.column_select = ctk.CTkComboBox(self.parent_frame, values=self.molecule_names, command = self.update_criteria_dropdown)
        self.column_select.grid(row=self.row_idx, column=1, padx=5, pady=5)
        self.column_select.set('Select')

        self.citeria_label = ctk.CTkLabel(self.parent_frame, text='Grouping Criteria')
        self.citeria_label.grid(row=self.row_idx, column=2, padx=10, sticky='e')
        self.criteria_select = ctk.CTkComboBox(self.parent_frame, values=[], command = self.update_value_input_type)
        self.criteria_select.grid(row=self.row_idx, column=3, padx=5, pady=5)
        self.criteria_select.set('Select')

        self.value_label = ctk.CTkLabel(self.parent_frame, text='Values')
        self.value_label.grid(row=self.row_idx, column=4, padx=10, sticky='e')
        self.value_select = None
        self.selected_values_label = None

        self.data_label = ctk.CTkLabel(self.parent_frame, text='Data Rows:')
        self.data_label.grid(row=self.row_idx, column=6, padx=10, sticky='e')
        self.data_rows_label = ctk.CTkLabel(self.parent_frame, text='0')
        self.data_rows_label.grid(row=self.row_idx, column=7, pady=5)

        self.delete_criteria_btn = ctk.CTkButton(self.parent_frame, text="Delete Criteria", fg_color='transparent', border_width=1, command=self.delete_criteria)
        self.delete_criteria_btn.grid(row=self.row_idx, column=8, padx=5, pady=5)

        # Disable all delete buttons except the last one
        self.update_delete_button_status()

    def delete_criteria(self):
        self.column_label.destroy()
        self.column_select.destroy()
        self.citeria_label.destroy()
        self.criteria_select.destroy()
        self.value_label.destroy()
        self.data_label.destroy()
        self.data_rows_label.destroy()
        self.delete_criteria_btn.destroy()
        if self.value_select:
            self.value_select.destroy()
        if  self.selected_values_label:
            self.selected_values_label.destroy()
        # Remove the criteria row from the parent's list
        for group_id, criteria_list in self.parent_class.criteria_rows.items():
            if self in criteria_list:
                self.parent_class.criteria_rows[group_id].remove(self)
                break
        # Handling the existing graph
        if hasattr(self.master.previewing_graph, 'canvas') and self.master.previewing_graph.canvas:
            widget = self.master.previewing_graph.canvas.get_tk_widget()
            if widget.winfo_exists():
                widget.destroy()
            self.master.previewing_graph.canvas = None  # Clear the reference

        for child in self.master.aggregate_groups_frame.winfo_children():
            child.destroy()

        # After deletion, update the status of the delete buttons
        self.update_delete_button_status()

        logger.info("Criteria Row deleted")

    def update_delete_button_status(self):
        # Get the list of all delete buttons
        delete_buttons = [child for child in self.parent_frame.winfo_children() if isinstance(child, ctk.CTkButton) and child.cget('text') == 'Delete Criteria']
        combo_boxes = [child for child in self.parent_frame.winfo_children() if isinstance(child, ctk.CTkComboBox)]

        # Disable all delete buttons except the last one
        if len(delete_buttons) > 1:
            for i, button in enumerate(delete_buttons):
                # Disable all except the last button
                if i != len(delete_buttons) - 1:
                    button.configure(state='disabled')
                else:
                    button.configure(state='normal')
        else:
            # If only one button remains, enable it
            delete_buttons[0].configure(state='disabled')

        # Disable all combo boxes except the ones in the last row
        if len(combo_boxes) > 2:  # More than two combo boxes
            for i, box in enumerate(combo_boxes):
                if i // 2 != (len(combo_boxes) // 2) - 1:  # If not the last row's combo boxes
                    box.configure(state='disabled')
                else:
                    box.configure(state='normal')
        elif combo_boxes:  # If only two combo boxes are left
            combo_boxes[0].configure(state='normal')
            combo_boxes[1].configure(state='normal')

    def update_criteria_dropdown(self, choice):
        if not self.group_name_entry.get():
            messagebox.showerror("Error", "Please populate the group name before selecting a grouping column.")
            self.column_select.set('Select')
            return
        # Determine criteria options based on the grouping column data type
        self.criteria_select.set('Select')
        self.data_rows_label.configure(text='0')
        if self.value_select:
            self.value_select.destroy()
        if  self.selected_values_label:
            self.selected_values_label.destroy()
        if pd.api.types.is_numeric_dtype(self.df[choice]):
            criteria_options = [">", "<", "=", "not ="]
        else:
            criteria_options = ["Equals", "Not Equal"]    

        self.criteria_select.configure(values=criteria_options)
    
        logger.info("Criteria dropdown is updated to (equals, not equals / (<, >, = and not =) based on the grouping column selected")

    def update_value_input_type(self, criteria):
        if self.value_select:
            self.value_select.destroy()
        if  self.selected_values_label:
            self.selected_values_label.destroy()
        selected_column = self.column_select.get()
        if criteria in ["Equals", "Not Equal"]:
            self.value_select = ctk.CTkButton(self.parent_frame, text="Click to Select", command=self.open_multiselect_dropdown)
            self.value_select.grid(row=self.row_idx, column=5, padx=5, pady=5)
            self.selected_values_label = ctk.CTkTextbox(self.parent_frame, width=200, height=50)
            self.selected_values_label.grid(row=self.row_idx + 1, column=5, padx=5, pady=5)
        else:
            group_name = self.group_name_entry.get()
            # Check if the group already exists else assign the input df
            matching_tuple_group = None
            if hasattr(self.master, 'filtered_dfs_next_filter') and self.master.filtered_dfs_next_filter:
                matching_tuple_group = next((item for item in self.master.filtered_dfs_next_filter if item[0] == group_name), None)
            df = matching_tuple_group[1] if matching_tuple_group else self.df
            # Check if df is a tuple and get the DataFrame inside it
            if isinstance(df, tuple):
                df = df[1] 
            
            self.unique_values = list(df[selected_column].unique())
            self.unique_values = [str(item) for item in self.unique_values]
            self.value_select = ctk.CTkComboBox(self.parent_frame, values=self.unique_values)
            self.value_select.grid(row=self.row_idx, column=5, padx=5, pady=5)
            self.value_select.set('Select')
            self.selected_values_label = None

        logger.info("Value dropdown is updated to multiselect or singleselect based on the grouping criteria")

    def open_multiselect_dropdown(self):
        group_name = self.group_name_entry.get()
        matching_tuple_group = None
        if hasattr(self.master, 'filtered_dfs_next_filter') and self.master.filtered_dfs_next_filter:
            matching_tuple_group = next((item for item in self.master.filtered_dfs_next_filter if item[0] == group_name), None)
        df = matching_tuple_group[1] if matching_tuple_group else self.df
        if isinstance(df, tuple):
            df = df[1] 

        options_selected = list(df[self.column_select.get()].unique())
        options_selected = [str(item) for item in options_selected]
        DropDownMulitSelect(self.parent_frame, options_selected, self.selected_values_label)

    # Retrieve the selected values
    
    def get_selected_criteria(self):
        try:
            selected_criteria = self.criteria_select.get()
            selected_column = self.column_select.get()

            if selected_criteria in ["Equals", "Not Equal"]:
                if self.selected_values_label:
                    raw_values = self.selected_values_label.get("2.0", "end-1c").strip()
                    value = [v.strip() for v in raw_values.split("\n") if v.strip()]
                else:
                    value = []
            else:
                if self.value_select:
                    value = self.value_select.get()
                else:
                    value = None
            
            return {
                "criteria": selected_criteria if selected_criteria != 'Select' else None,
                "column": selected_column if selected_column != 'Select' else None,
                "value": value if value else []
            }
        except Exception as e:
            # messagebox.showerror("Error", f"An error occurred while retrieving selected criteria: {e}")
            return {
            "criteria": "None",
            "column": "None",
            "value": []
        }
        
    # Method to update the data rows label
    def update_data_rows_label(self, num_rows):
        if self.data_rows_label and self.data_rows_label.winfo_exists():
            self.data_rows_label.configure(text=str(num_rows))
        # self.data_rows_label.configure(text=str(num_rows))
        logger.info("Data Rows label updated")
    
    def disable(self):
        self.column_select.configure(state='disabled')
        self.criteria_select.configure(state='disabled')
        self.value_select.configure(state='disabled')
        self.delete_criteria_btn.configure(state='disabled')
    
    def enable(self):
        self.column_select.configure(state='normal')
        self.criteria_select.configure(state='normal')
        self.value_select.configure(state='normal')
        self.delete_criteria_btn.configure(state='normal')