"""
Log Handlers

This module contains utility functions to set up logging consistently.
"""

import logging
from flask import Flask


def init_logging(app: Flask, logger_name: str) -> None:
    """
    Set up logging for a Flask app in production.

    Ensures log propagation is disabled, adopts the Gunicorn logger if present,
    and applies a consistent log format.
    """
    # Prevent Flask from propagating logs to the root logger
    app.logger.propagate = False

    # Get Gunicorn logger if available
    gunicorn_logger = logging.getLogger(logger_name)
    if gunicorn_logger.handlers:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    # Define a consistent log format
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s",
        "%Y-%m-%d %H:%M:%S %z",
    )

    # Apply formatter to all handlers
    for handler in app.logger.handlers:
        handler.setFormatter(formatter)

    app.logger.info("Logging handler established")




