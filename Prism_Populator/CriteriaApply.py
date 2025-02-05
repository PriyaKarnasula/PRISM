import pandas as pd
import customtkinter as ctk
from tkinter import messagebox
from tkinter import filedialog
from MoveUpDown import MoveUpDown
from CTkTable import *
import logging

logger = logging.getLogger(__name__)

class CriteriaApplication:
    def __init__(self, parent):
        self.parent = parent

    def apply_criteria(self):
        if not self.parent.selected_values_label:
            messagebox.showerror("Error", "Please select molecules before applying filters.")
            return
        if not hasattr(self.parent, 'group_frame') or not self.parent.group_frame:
            messagebox.showerror("Error", "No groups created yet. Please create groups first.")
            return
        
        # Check if all groups have a name
        for group_frame in self.parent.group_frame:
            for child in group_frame.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    for inner_child in child.winfo_children():
                        if isinstance(inner_child, ctk.CTkEntry):
                            if not inner_child.get().strip():
                                messagebox.showerror("Error", "Please enter all the group names before applying filters.")
                                return

        # Clean up criteria rows before applying criteria
        for group_id in self.parent.criteria_rows.keys():
            self.parent.criteria_rows[group_id] = [
                row for row in self.parent.criteria_rows[group_id] if row is not None
            ]

        group_data = []
        self.parent.filtered_dfs = []
        self.parent.filtered_dfs_next_filter = []
        criteria_data = []  # List to hold criteria information for the final DataFrame
        group_names_list = []  # List to store group names for MoveUpDown

        # Get the selected molecules
        selected_molecules = self.parent.selected_values_label.get("2.0", "end-1c").strip()
        selected_molecules = [m.strip() for m in selected_molecules.split("\n")  if m.strip()]

        logger.info("Selected molecules for applying criteria: %s", selected_molecules)

        if not selected_molecules:
            messagebox.showerror("Error", "Please select molecules before applying filters.")
            return
        
        for group_id, group_frame in enumerate(self.parent.group_frame):
            # Adjusting group IDs to match the existing keys in criteria_rows
            actual_group_ids = list(self.parent.criteria_rows.keys())
            if group_id >= len(actual_group_ids):
                continue

            actual_group_id = actual_group_ids[group_id]
    
            group_info = {"group_name": None, "criteria": []}
            filtered_df = self.parent.df.copy()

            # Find group name entry and criteria frames within the group frame
            for child in group_frame.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    for inner_child in child.winfo_children():
                        if isinstance(inner_child, ctk.CTkEntry):
                            group_info["group_name"] = inner_child.get()
                            logger.info("Group Name: %s", group_info["group_name"])

            # Get criteria for the current group and apply them
            if actual_group_id in self.parent.criteria_rows:
                for criteria_row in self.parent.criteria_rows[actual_group_id]:
                    if criteria_row is None:
                        continue
                    if criteria_row and criteria_row.winfo_exists():
                        selected_criteria = criteria_row.get_selected_criteria()
                    # Check if the criteria is valid
                    if not criteria_row.winfo_exists():
                        continue
                    if (selected_criteria["column"] in ['None', ""] or selected_criteria["criteria"] in ['None', ""]):
                        continue                        
                    group_info["criteria"].append(selected_criteria)
                    # Apply criteria
                    column = selected_criteria["column"]
                    value = selected_criteria["value"]
                    crit_type = selected_criteria["criteria"]

                    if crit_type == "Equals":
                        if column in filtered_df.columns:
                            nan_filter = filtered_df[column].isna()
                            value_filter = filtered_df[column].isin([v for v in value if v != "nan"])
                            combined_filter = value_filter | (nan_filter & ("nan" in value))
                            filtered_df = filtered_df[combined_filter]
                    elif crit_type == "Not Equal":
                        if column in filtered_df.columns:
                            nan_filter = filtered_df[column].isna()
                            value_filter = filtered_df[column].isin([v for v in value if v != "nan"])
                            combined_filter = ~value_filter & (~nan_filter | ("nan" not in value))
                            filtered_df = filtered_df[combined_filter]
                    elif crit_type == ">":
                        if column in filtered_df.columns:
                            filtered_df = filtered_df[filtered_df[column] > float(value)]
                    elif crit_type == "<":
                        if column in filtered_df.columns:
                            filtered_df = filtered_df[filtered_df[column] < float(value)]
                    elif crit_type == "=":
                        if column in filtered_df.columns:
                            if value == "nan":
                                filtered_df = filtered_df[filtered_df[column].isna()]
                            else:
                                filtered_df = filtered_df[filtered_df[column] == float(value)]
                            # filtered_df = filtered_df[filtered_df[column] == float(value)]
                    elif crit_type == "not =":
                        if column in filtered_df.columns:
                            if value == "nan":
                                filtered_df = filtered_df[~filtered_df[column].isna()]
                            else:
                                filtered_df = filtered_df[filtered_df[column] != float(value)]
                            # filtered_df = filtered_df[filtered_df[column] != float(value)]

                    # Get the number of rows after applying the filter
                    num_rows = filtered_df.shape[0]

                    # Update the GUI label with the number of rows
                    criteria_row.update_data_rows_label(num_rows)

                    # Add criteria information and row count to the criteria_data list
                    criteria_data.append({
                        "Group Name": group_info["group_name"],
                        "Grouping Column": selected_criteria["column"],
                        "Grouping Criteria": selected_criteria["criteria"],
                        "Values": ", ".join(selected_criteria["value"]) if isinstance(selected_criteria["value"], list) else selected_criteria["value"],
                        "Number of Rows": filtered_df.shape[0]
                    })

            group_data.append(group_info)

            # Filter the DataFrame to include only the selected molecules
            filtered_df_for_next_filter = filtered_df.copy()
            if selected_molecules:
                valid_columns = [col for col in selected_molecules if col in self.parent.df.columns]
                filtered_df = filtered_df[valid_columns]

            if group_info["group_name"]:
                self.parent.filtered_dfs.append((group_info["group_name"], filtered_df))
                self.parent.filtered_dfs_next_filter.append((group_info["group_name"], filtered_df_for_next_filter))
                group_names_list.append(group_info["group_name"])  # Add group name to the list

        logger.info("Filtered DataFrames created successfully")
        # print("Filtered DataFrames created successfully.")
        # print(self.parent.filtered_dfs_next_filter)

        # Create and print the final DataFrame with criteria information
        self.parent.criteria_df = pd.DataFrame(criteria_data)
        # print("Criteria DataFrame:\n", self.parent.criteria_df)
        logger.info("Criteria DataFrame created successfully")

        # Frame for displaying group names
        self.group_names_frame = ctk.CTkScrollableFrame(self.parent.aggregate_groups_frame)
        self.group_names_frame.grid(row=0, column=0, padx=10, sticky="ew") 

        # Prepare the data for the CTkTable
        group_names = ["Group Name", "Number of Rows"]  # Column headers
        table_data = [group_names]  

        for idx, group_info in enumerate(group_data):
            group_name = group_info["group_name"]
            number_of_rows = self.parent.filtered_dfs[idx][1].shape[0]
            table_data.append([group_name, number_of_rows])

        # Create the CTkTable with the prepared data
        table = CTkTable(master=self.group_names_frame, row=len(table_data), column=len(group_names), values=table_data, wraplength=100, hover_color = '#0096FF')
        table.grid(row=0, column=0, padx=5, pady=5)

        # Scrollable Frame for moving groups up and down       
        self.parent.up_down_frame = ctk.CTkFrame(self.parent.aggregate_groups_frame)
        self.parent.up_down_frame.grid(row=1, column=0, padx=10, pady=10)
        # print(group_names_list)
        updown_object = MoveUpDown(self.parent, self.parent.up_down_frame, group_names_list)
        updown_object.grid(row=0, column=0, sticky = 'ew')