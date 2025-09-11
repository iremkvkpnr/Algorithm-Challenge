"""Logging utility for VRP API."""

import logging
import sys
from datetime import datetime

class VRPFormatter(logging.Formatter):
    def format(self, record):
        record.timestamp = datetime.utcnow().isoformat() + 'Z'

        colors = {
            'DEBUG': '\033[36m',
            'INFO': '\033[32m',
            'WARNING': '\033[33m',
            'ERROR': '\033[31m',
            'CRITICAL': '\033[35m'
        }
        reset = '\033[0m'
        color = colors.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{reset}"
        return super().format(record)


def setup_logger(name, level="INFO", fmt=None):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper()))
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))

    if fmt is None:
        fmt = "%(timestamp)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"

    handler.setFormatter(VRPFormatter(fmt))
    logger.addHandler(handler)
    return logger


def get_logger(name):
    return setup_logger(name)


def get_api_logger():
    return get_logger("vrp.api")


def get_service_logger():
    return get_logger("vrp.service")


def get_solver_logger():
    return get_logger("vrp.solver")
