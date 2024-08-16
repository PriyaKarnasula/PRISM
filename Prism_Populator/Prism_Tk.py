import logging
from logging import handlers
import multiprocessing
import os
import sys
import customtkinter as ctk
from Grouping import Groups
from log_listener import listener_process

logger = logging.getLogger(__name__) 

def root_configurer(queue):
    h = handlers.QueueHandler(queue)
    root = logging.getLogger()
    root.addHandler(h)
    root.setLevel(logging.INFO)
    
class Prism(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("PRISM")
        self.geometry("2500x1000")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.parent_frame = ctk.CTkFrame(self)
        self.parent_frame.grid(row=0,column=0,sticky="nsew")
        self.parent_frame.grid_columnconfigure(0, weight=1)
        self.parent_frame.grid_rowconfigure(0, weight=1)

        self.nav_frame = ctk.CTkFrame(self.parent_frame)
        self.nav_frame.grid(row=0,column=0,sticky="nsew")
        self.nav_frame.columnconfigure(0, weight=1)
        self.nav_frame.rowconfigure(0, weight=1)

        self.meta_frame = Groups(self.parent_frame, self.nav_frame)
        self.meta_frame.columnconfigure(0, weight=1)
        self.meta_frame.rowconfigure(0, weight=1)

        self.write_num_children_to_logs()

    def write_num_children_to_logs(self):

        def count_all_children(widget):
            """
            Recursively counts all descendants of a given widget.
            """
            count = len(widget.winfo_children())
            for child in widget.winfo_children():
                count += count_all_children(child)
            return count

        # Assuming self.parent_frame is your root widget from which you want to start counting
        total_children = count_all_children(self.parent_frame)

        logger.info("Frequent_checker :: Total children {}".format(str(total_children)))
        self.after(10000, self.write_num_children_to_logs)

if __name__ == "__main__":
    
    ENVIRONMENT = "NONE"
    try :
        base_path = sys._MEIPASS
        log_directory= os.path.join(base_path, "logs")
        ENVIRONMENT = "EXE"
    except Exception as e:
        log_directory = os.path.abspath(r"/Users/priyakarnasula/Documents/GitHub/PRISM/logs")
        ENVIRONMENT = "DEV"

    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    multiprocessing.set_start_method('spawn')
    multiprocessing.freeze_support()
    log_queue = multiprocessing.Queue(-1)
    listener = multiprocessing.Process(target=listener_process, args=(log_queue, log_directory))
    listener.start()
    root_configurer(log_queue)

    logger.info("Starting the application")
    logger.info("Running Environment: {}".format(ENVIRONMENT))

    app = Prism()
    app.mainloop()

    logger.info("teminating log listener process")
    listener.terminate()