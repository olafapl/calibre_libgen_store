import sys
import logging

NAME = "Library Genesis store"
LOG_LEVEL = logging.DEBUG

formatter = logging.Formatter(fmt=f"%(asctime)s [%(levelname)s] {NAME} - %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger = logging.getLogger(NAME)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
