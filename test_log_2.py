import os
import logging
import requests              # third-party example
from logger_factory import setup_logging
from test_log import do_something

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.abspath(__file__))

    #  ──> HERE we choose **INFO** for our code & **WARNING** for everything else
    logfile = setup_logging(
        "test",
        #project_root,
        #project_console_level=logging.ERROR,
        #other_console_level=logging.INFO,
    )
    print(f"\n📓  Writing your code’s DEBUG+ logs to {logfile}\n")

    # — YOUR code —  (INFO+ → console, DEBUG+ → file)
    do_something()

    # — A real library log —  
    # configure urllib3 (used by requests) to INFO
    logging.getLogger("urllib3").setLevel(logging.DEBUG)
    requests.get("https://httpbin.org/get", timeout=100)

    # — If you manually do logging.getLogger("requests").info(...) from here,  
    #   it still looks like *your* code (because it originates in this file)
    #   so it will follow the “project” handlers.  Library-originated logs 
    #   show correctly in the console at WARNING+.
    
    print("\nDone.")