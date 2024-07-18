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
        self.title("Prism")
        self.geometry("2500x1000")

        self.parent_frame = ctk.CTkFrame(self)
        self.parent_frame.grid(row=0,column=0,sticky="nsew")

        self.nav_frame = ctk.CTkFrame(self.parent_frame)
        self.nav_frame.grid(row=0,column=0,sticky="new")

        self.meta_frame = Groups(self.parent_frame, self.nav_frame)
        self.meta_frame.grid(row=1, column=0, sticky="nsew",pady=(5,0), padx=(0,0))

if __name__ == "__main__":

    app = Prism()
    app.mainloop()
    
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