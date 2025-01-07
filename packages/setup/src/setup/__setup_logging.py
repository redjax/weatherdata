from __future__ import annotations

import sys

from loguru import logger

def filter_info_debug_warning(record):
    """Filter out INFO, DEBUG, and WARNING messages.
    
    Params:
        record (dict): The log record to filter.
    
    Returns:
        bool: True if the log record should be filtered out, False otherwise.

    """
    return record["level"].name in ["WARNING", "INFO", "DEBUG"]

def filter_debug_only(record):
    """Filter out INFO, DEBUG, and WARNING messages.
    
    Params:
        record (dict): The log record to filter.
    
    Returns:
        bool: True if the log record should be filtered out, False otherwise.

    """
    return record["level"].name == "DEBUG"

def filter_error_only(record):
    """Filter out INFO, DEBUG, and WARNING messages.
    
    Params:
        record (dict): The log record to filter.
    
    Returns:
        bool: True if the log record should be filtered out, False otherwise.

    """
    return record["level"].name == "ERROR"

def filter_trace_only(record):
    """Filter out INFO, DEBUG, and WARNING messages.
    
    Params:
        record (dict): The log record to filter.
    
    Returns:
        bool: True if the log record should be filtered out, False otherwise.

    """
    return record["level"].name == "TRACE"

def filter_all_errors(record):
    """Filter out INFO, DEBUG, and WARNING messages.
    
    Params:
        record (dict): The log record to filter.
    
    Returns:
        bool: True if the log record should be filtered out, False otherwise.

    """
    return record["level"].name in ["ERROR", "TRACE"]

def setup_loguru_logging(
    log_level: str = "INFO",
    enable_loggers: list[str] = ["auto_weather"],
    add_file_logger: bool = False,
    app_log_file: str = "logs/app.log",
    add_error_file_logger: bool = False,
    error_log_file: str = "logs/error.log",
    colorize: bool = False,
    retention: int = 3,
    rotation: str = "15 MB",
):
    """Setup loguru logging.

    Params:
        log_level (str): The log level to use.
        enable_loggers (list[str]): A list of loggers to enable.
        add_file_logger (bool): If `True`, add a file logger to the log.
        add_error_file_logger (bool): If `True`, add a file logger to the log for errors.
        colorize (bool): If `True`, colorize the log output.
    """
    logger.remove(0)
    logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD HH:mm:ss} | [{level}] | ({module}.{function}:{line}) | > {message}",
        level=log_level,
        colorize=colorize
    )

    if enable_loggers:
        for _logger in enable_loggers:
            logger.enable(_logger)

    if add_file_logger:
        logger.add(app_log_file, retention=retention, rotation=rotation, level="DEBUG")

    if add_error_file_logger:
        logger.add(error_log_file, retention=retention, rotation=rotation, level="ERROR")
