import pandas as pd
import customtkinter as ctk
from tkinter import messagebox
from tkinter import filedialog

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
        group_data = []
        self.parent.filtered_dfs = []
        criteria_data = []  # List to hold criteria information for the final DataFrame

        # Get the selected molecules
        selected_molecules = self.parent.selected_values_label.get("2.0", "end-1c").strip()
        selected_molecules = [m.strip() for m in selected_molecules.split("\n")  if m.strip()]

        for group_id, group_frame in enumerate(self.parent.group_frame):
            group_info = {"group_name": None, "criteria": []}
            filtered_df = self.parent.df.copy()

            # Find group name entry and criteria frames within the group frame
            for child in group_frame.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    for inner_child in child.winfo_children():
                        if isinstance(inner_child, ctk.CTkEntry):
                            group_info["group_name"] = inner_child.get()

            # Get criteria for the current group and apply them
            if group_id + 1 in self.parent.criteria_rows:
                for criteria_row in self.parent.criteria_rows[group_id + 1]:
                    selected_criteria = criteria_row.get_selected_criteria()
                    group_info["criteria"].append(selected_criteria)

                    # Apply criteria
                    column = selected_criteria["column"]
                    value = selected_criteria["value"]
                    crit_type = selected_criteria["criteria"]
        
                    if crit_type == "Equals":
                        if column in filtered_df.columns:
                            filtered_df = filtered_df[filtered_df[column].isin(value)]
                    elif crit_type == "Not Equal":
                        if column in filtered_df.columns:
                            filtered_df = filtered_df[~filtered_df[column].isin(value)]
                    elif crit_type == ">":
                        if column in filtered_df.columns:
                            filtered_df = filtered_df[filtered_df[column] > float(value)]
                    elif crit_type == "<":
                        if column in filtered_df.columns:
                            filtered_df = filtered_df[filtered_df[column] < float(value)]
                    elif crit_type == "=":
                        if column in filtered_df.columns:
                            filtered_df = filtered_df[filtered_df[column] == float(value)]
                    elif crit_type == "not =":
                        if column in filtered_df.columns:
                            filtered_df = filtered_df[filtered_df[column] != float(value)]

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
            if selected_molecules:
                valid_columns = [col for col in selected_molecules if col in self.parent.df.columns]
                filtered_df = filtered_df[valid_columns]

            if group_info["group_name"]:
                self.parent.filtered_dfs.append((group_info["group_name"], filtered_df))
                print(f"Filtered DataFrame for group {group_info['group_name']}:\n", filtered_df)

        print("Filtered DataFrames created successfully.")

        # Create and print the final DataFrame with criteria information
        self.parent.criteria_df = pd.DataFrame(criteria_data)
        print("Criteria DataFrame:\n", self.parent.criteria_df)
