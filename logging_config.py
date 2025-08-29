# logging_config.py
import logging

LOG_FILE = "app.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,  # capture everything
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="a"          # append to the log file (default)
)
