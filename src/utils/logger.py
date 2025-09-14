"""Logging utility for VRP API."""

import logging
import sys


def setup_logger(name, level="INFO"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper()))
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_logger(name):
    return setup_logger(name)


def get_service_logger():
    return get_logger("vrp.service")
