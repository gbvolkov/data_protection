import logging
import sys


def set_logging(app_name, min_level=logging.DEBUG):
    # Create handlers
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)  # capture all levels

    # 2. Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(min_level)  # what goes to the screen

    file_handler = logging.FileHandler(f"logs/{app_name}.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # what goes to the file

    # 3. Create and set a formatter (same or different per handler)
    fmt = "%(asctime)s — %(name)s — %(levelname)s — %(message)s"
    formatter = logging.Formatter(fmt)

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 4. Attach handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


    # Create a formatter and set it on both
    #fmt = logging.Formatter("%(asctime)s — %(levelname)s — %(name)s — %(message)s")
    #console_h.setFormatter(fmt)
    #file_h.setFormatter(fmt)

    # Configure the root logger
    #logging.basicConfig(
    #    level=max_level,            # root level
    #    handlers=[console_h, file_h]    # both console & file
    #)


if __name__ == '__main__':
    import time
    import threading

    thread_id = threading.get_ident()
    timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    log_name = f"test_{timestamp}_{thread_id}"


    logging.basicConfig(level=logging.DEBUG)
    
    set_logging(log_name, logging.WARNING)
    logger = logging.getLogger(log_name)

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning")

