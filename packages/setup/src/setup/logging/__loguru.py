from __future__ import annotations

import sys

from loguru import logger
import logging
import settings

__all__ = ["setup_loguru_logging", "setup_fastapi_logging", "setup_uvicorn_logging"]

LOGGING_SETTINGS = settings.get_namespace("logging")


ALLOWED_LOGGERS = {
    "uvicorn",
    "uvicorn.error",
    "uvicorn.access",
    "fastapi",
    "cgg_api",
    "__main__",
    "uvicorn.asgi",
    "uvicorn.lifespan",
}


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
    enable_loggers: list[str] = [],
    add_file_logger: bool = False,
    app_log_file: str = "logs/app.log",
    add_error_file_logger: bool = False,
    error_log_file: str = "logs/error.log",
    colorize: bool = False,
    retention: int = 3,
    rotation: str = "15 MB",
    log_fmt: str = "detailed",
):
    """Setup loguru logging.

    Params:
        log_level (str): The log level to use.
        enable_loggers (list[str]): A list of loggers to enable.
        add_file_logger (bool): If `True`, add a file logger to the log.
        add_error_file_logger (bool): If `True`, add a file logger to the log for errors.
        colorize (bool): If `True`, colorize the log output.
    """
    valid_log_fmts: list[str] = ["basic", "detailed"]

    fmt_basic: str = "{time:YY-MM-DD HH:mm:ss} [<level>{level}</level>]: {message}"
    fmt_basic_color: str = (
        "<blue>{time:YY-MM-DD HH:mm:ss}</> [<level>{level}</level>]: {message}"
    )

    fmt_detailed: str = (
        "<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> | [<level>{level}</level>] | (<level>{module}.{function}:{line}</level>) | > {message}"
    )
    fmt_detailed_color: str = (
        "<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> | [<level>{level}</level>] | (<level>{module}.{function}:{line}</level>) | > {message}"
    )

    match log_fmt.lower():
        case "basic":
            if colorize:
                fmt = fmt_basic_color
            else:
                fmt = fmt_basic
        case "detailed":
            if colorize:
                fmt = fmt_detailed_color
            else:
                fmt = fmt_detailed
        case _:
            raise ValueError(
                f"Unknown log_fmt: '{log_fmt}'. Must be one of {valid_log_fmts}"
            )

    logger.remove(0)
    logger.add(sys.stderr, format=fmt, level=log_level, colorize=colorize)

    if enable_loggers:
        for _logger in enable_loggers:
            logger.enable(_logger)

    if add_file_logger:
        logger.add(
            app_log_file,
            format=fmt,
            retention=retention,
            rotation=rotation,
            level="DEBUG",
        )

    if add_error_file_logger:
        logger.add(
            error_log_file,
            format=fmt,
            retention=retention,
            rotation=rotation,
            level="ERROR",
        )


def setup_fastapi_logging(
    async_enqueue: bool = True, diagnose: bool = False, backtrace: bool = True
):
    LOG_FMT = "<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> | <level>{level: <8}</level> :: {message}"
    if LOGGING_SETTINGS.get("LOG_LEVEL") == "DEBUG":
        LOG_FMT = "<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> | <level>{level: <8}</level> | <level>({file}.{module}.{function}:{line})</level> :: {message}"

    class InterceptHandler(logging.Handler):
        """Intercept stdlib logging."""

        def emit(self, record):
            logger_opt = logger.opt(depth=6, exception=record.exc_info)
            logger_opt.log(record.levelname, record.getMessage())

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    ## Configure Loguru
    logger.remove()
    logger.add(
        sys.stderr,
        format=LOG_FMT,
        enqueue=async_enqueue,
        diagnose=diagnose,
        backtrace=backtrace,
    )


def setup_uvicorn_logging(
    log_level: str = "INFO",
    async_enqueue: bool = True,
    diagnose: bool = False,
    backtrace: bool = True,
    suppress_uvicorn_access: bool = False,
    suppress_uvicorn_reload: bool = False,
):
    LOG_FMT = "<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> | <level>{level: <8}</level> :: {message}"
    if log_level == "DEBUG":
        LOG_FMT = "<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> | <level>{level: <8}</level> | <level>({file}.{module}.{function}:{line})</level> :: {message}"

    class InterceptHandler(logging.Handler):
        def emit(self, record):
            ## Skip logs from Python's logging internals
            if record.name.startswith("logging"):
                return
            ## Only allow logs from allowed loggers
            if record.name not in ALLOWED_LOGGERS:
                return
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            ## Set depth for accurate caller info
            frame, depth = logging.currentframe(), 2
            while frame and frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1
            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    ## Remove all existing handlers
    logging.root.handlers = []
    ## Set root logger to lowest level
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    ## Remove default Loguru handler and add ours
    logger.remove()
    logger.add(
        sys.stderr,
        format=LOG_FMT,
        level=log_level,
        enqueue=async_enqueue,
        diagnose=diagnose,
        backtrace=backtrace,
    )

    ## Optionally suppress noisy Uvicorn loggers
    if suppress_uvicorn_access:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    if suppress_uvicorn_reload:
        logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.reload").setLevel(logging.WARNING)