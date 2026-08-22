import logging
import os.path
import sys
from time import strftime

logger = logging.getLogger("GRYT")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s %(name)s [%(levelname)s] %(message)s")

# Console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File
LOGFILE_PATH = (
    os.path.dirname(os.path.abspath(__file__))
    + f"/../logs/log_[{strftime('%Y-%m-%d_%H-%M-%S')}].txt"
)
file_handler = logging.FileHandler(LOGFILE_PATH)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# Exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    logger.error(
        msg="Unhandled exception.", exc_info=(exc_type, exc_value, exc_traceback)
    )


sys.excepthook = handle_exception

# First log
logger.info("Setup logger.")
