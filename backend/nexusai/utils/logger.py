import logging
import sys


def setup_logger(name: str = "nexusai", level: int | None = None) -> logging.Logger:
    # Create logger
    logger = logging.getLogger(name)

    # Set level
    logger.setLevel(level or logging.INFO)

    # Create console handler and set level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Create formatter with filename and line number
    formatter = logging.Formatter(
        "%(levelname)s - %(asctime)s - %(name)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Add formatter to handler
    console_handler.setFormatter(formatter)

    # Add handler to logger if it doesn't already have handlers
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger


# Create default logger instance
logger = setup_logger()
