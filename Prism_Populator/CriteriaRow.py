import customtkinter as ctk
import pandas as pd
from MultiselectDropdown import DropDownMulitSelect
from tkinter import messagebox
from GraphPreview import PreviewGraph  # Import the new class

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
            self.unique_values = list(self.df[selected_column].unique())
            self.unique_values = [str(item) for item in self.unique_values]
            self.value_select = ctk.CTkComboBox(self.parent_frame, values=self.unique_values)
            self.value_select.grid(row=self.row_idx, column=5, padx=5, pady=5)
            self.value_select.set('Select')
            self.selected_values_label = None

    def open_multiselect_dropdown(self):
        options_selected = list(self.df[self.column_select.get()].unique())
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
            messagebox.showerror("Error", f"An error occurred while retrieving selected criteria: {e}")
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