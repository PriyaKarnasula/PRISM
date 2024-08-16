import logging
import customtkinter as ctk
import logging

logger = logging.getLogger(__name__)

class MoveUpDown(ctk.CTkFrame):
    def __init__(self, parent, master, lst_items):
        super().__init__(master)
        
        self.parent = parent
        self.lst_items = lst_items
        self.lst_checkboxes = []
        self.create_widgets()

    def create_lst_checkboxes(self):
        # destroying children of items_scrollable_frame 
        for widget in self.items_scrollable_frame.winfo_children():
            widget.destroy()
        self.lst_checkboxes = []
        for item in self.lst_items:
            self.item = ctk.CTkCheckBox(self.items_scrollable_frame, text=item)
            self.item.grid(row=self.lst_items.index(item), column=0, padx=5, pady=5, sticky="ew")
            self.lst_checkboxes.append(self.item)

        logger.info("Checkboxes are created for moving groups up and down.")

    def create_widgets(self):
        self.parent_frame = ctk.CTkFrame(self)
        self.parent_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.items_scrollable_frame = ctk.CTkScrollableFrame(self.parent_frame)
        self.items_scrollable_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.create_lst_checkboxes()
        self.move_up_button = ctk.CTkButton(self.parent_frame, text="Move Up", fg_color='transparent', border_width = 1, command=self.move_up)
        self.move_up_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.move_down_button = ctk.CTkButton(self.parent_frame, text="Move Down",  fg_color='transparent', border_width = 1, command=self.move_down)
        self.move_down_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

    def get_selected_box_id(self):
        for cbox, item_name in zip(self.lst_checkboxes, self.lst_items):
            if cbox.get() ==1:
                return item_name
            
        logger.info("Selected group to move: %s", item_name)
            
    def move_up(self):      
        selected_item = self.get_selected_box_id()
        selected_item_index = self.lst_items.index(selected_item)
        if selected_item_index == 0:
            return
        else:
            self.lst_items[selected_item_index], self.lst_items[selected_item_index-1] = self.lst_items[selected_item_index-1], self.lst_items[selected_item_index]
            self.create_lst_checkboxes()
        new_order = self.lst_items
        # Reorder filtered_dfs according to the new order
        self.parent.filtered_dfs = [df for group_name in new_order for df in self.parent.filtered_dfs if df[0] == group_name]
        # print("Filtered DataFrames reordered successfully.")
        # print(self.parent.filtered_dfs)
        # self.clear_selection()
        logger.info("Group %s is moved up.", selected_item)

    def move_down(self):
        selected_item = self.get_selected_box_id()
        selected_item_index = self.lst_items.index(selected_item)
        if selected_item_index == len(self.lst_items)-1:
            return
        else:
            self.lst_items[selected_item_index], self.lst_items[selected_item_index+1] = self.lst_items[selected_item_index+1], self.lst_items[selected_item_index]
            self.create_lst_checkboxes()
        new_order = self.lst_items
        # Reorder filtered_dfs according to the new order
        self.parent.filtered_dfs = [df for group_name in new_order for df in self.parent.filtered_dfs if df[0] == group_name]
        # print("Filtered DataFrames reordered successfully.")
        # print(self.parent.filtered_dfs)
        # self.clear_selection()
        logger.info("Group %s is moved down.", selected_item)

    def get_selected_order(self):
        return self.lst_items

    def clear_selection(self):
        "This function is used to clear the selection"
        # logging.info("Clearing the selection")
        for cbox in self.lst_checkboxes:
            cbox.deselect() 
        self.selected_files = []
        # self.display_selected_files()
        
class APP(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title('Dry App')
        self.geometry('200x200')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.lst_items = ['Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5', 'Item 6', 'Item 7', 'Item 8', 'Item 9', 'Item 10']
        self.move_up_down = MoveUpDown(self, self.lst_items)
        self.move_up_down.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        # Configure logging
        logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    def callback(self):
        logging.info('Button clicked')
        # print('Button clicked')

if __name__ == '__main__':
    app = APP()
    app.mainloop()