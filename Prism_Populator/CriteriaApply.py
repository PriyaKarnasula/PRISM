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
        
        # Clean up criteria rows before applying criteria
        for group_id in self.parent.criteria_rows.keys():
            self.parent.criteria_rows[group_id] = [
                row for row in self.parent.criteria_rows[group_id] if row is not None
            ]

        group_data = []
        self.parent.filtered_dfs = []
        criteria_data = []  # List to hold criteria information for the final DataFrame

        # Get the selected molecules
        selected_molecules = self.parent.selected_values_label.get("2.0", "end-1c").strip()
        selected_molecules = [m.strip() for m in selected_molecules.split("\n")  if m.strip()]

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

        print("Filtered DataFrames created successfully.")
        # print(self.parent.filtered_dfs)
        # Create and print the final DataFrame with criteria information
        self.parent.criteria_df = pd.DataFrame(criteria_data)
        print("Criteria DataFrame:\n", self.parent.criteria_df)

        # Frame for displaying group names
        self.group_names_frame = ctk.CTkFrame(self.parent.parent_group_frame)
        self.group_names_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 10), pady=(10, 10))
        ctk.CTkLabel(self.group_names_frame, text="Group Name").grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkLabel(self.group_names_frame, text="Number of Rows").grid(row=0, column=1, padx=10, pady=10)
        for idx, group_info in enumerate(group_data):
            ctk.CTkLabel(self.group_names_frame, text=group_info["group_name"]).grid(row=idx+1, column=0, padx=10, pady=10)
            ctk.CTkLabel(self.group_names_frame, text=str(self.parent.filtered_dfs[idx][1].shape[0])).grid(row=idx+1, column=1, padx=10, pady=10)        
