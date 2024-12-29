from __future__ import annotations

import sys

from loguru import logger

def filter_info_debug_warning(record):
    return record["level"].name in ["WARNING", "INFO", "DEBUG"]

def filter_debug_only(record):
    return record["level"].name == "DEBUG"

def filter_error_only(record):
    return record["level"].name == "ERROR"

def filter_trace_only(record):
    return record["level"].name == "TRACE"

def filter_all_errors(record):
    return record["level"].name in ["ERROR", "TRACE"]

def setup_loguru_logging(
    log_level: str = "INFO",
    enable_loggers: list[str] = ["auto_weather"],
    add_file_logger: bool = False,
    add_error_file_logger: bool = False,
    colorize: bool = False
):
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
        logger.add("logs/app.log", retention=3, rotation="15 MB", level="DEBUG")

    if add_error_file_logger:
        logger.add("logs/error.log", retention=3, rotation="15 MB", level="ERROR")
