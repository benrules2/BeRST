import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def info(message):
    logging.info(message)

def debug(message):
    logging.debug(message)

def error(message):
    logging.error(message)