from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
import typing as t

__all__ = [
    "setup_logging",
    "get_rotating_file_handler",
    "get_timed_rotating_file_handler",
]

valid_log_levels: t.List[str] = [
    "NOTSET",
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]


def get_rotating_file_handler(
    filename: str,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    encoding: str = "utf-8",
) -> RotatingFileHandler:
    """Create a size-based rotating file handler.

    Args:
        filename: The name of the log file.
        max_bytes: The maximum size of the log file before it gets rotated.
        backup_count: The number of backup files to keep.
        encoding: The encoding to use for the log file.

    Returns:
        A RotatingFileHandler instance.

    """
    file_path = Path(filename)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        filename, maxBytes=max_bytes, backupCount=backup_count, encoding=encoding
    )
    return handler


def get_timed_rotating_file_handler(
    filename: str,
    when: str = "midnight",
    interval: int = 1,
    backup_count: int = 7,
    encoding: str = "utf-8",
) -> TimedRotatingFileHandler:
    """Create a time-based rotating file handler.

    Args:
        filename: The name of the log file.
        when: The type of interval. Can be 'S' (seconds), 'M' (minutes), 'H' (hours),
              'D' (days), 'W0'-'W6' (weekday, 0=Monday), 'midnight'.
        interval: The interval count.
        backup_count: The number of backup files to keep.
        encoding: The encoding to use for the log file.

    Returns:
        A TimedRotatingFileHandler instance.

    """
    file_path = Path(filename)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    handler = TimedRotatingFileHandler(
        filename,
        when=when,
        interval=interval,
        backupCount=backup_count,
        encoding=encoding,
    )
    return handler


def setup_logging(
    level: t.Union[str, int] = logging.WARNING,
    filename: t.Optional[str] = None,
    error_filename: t.Optional[str] = None,
    fmt: str = "%(asctime)s [%(levelname)s] :: %(message)s",
    debug_fmt: str = "%(asctime)s | [%(levelname)s] | %(name)s:%(lineno)s :: %(message)s",
    datefmt: str = "%H:%M:%S",
    debug_datefmt: str = "%Y-%m-%dT%H:%M:%SZ",
    handlers: t.Optional[t.List[logging.Handler]] = None,
    silence_loggers: t.Optional[t.List[str]] = None,
    add_stream_handler: bool = True,
    use_rotating_handler: bool = True,
) -> None:
    """Set up logging configuration with enhanced features.

    Args:
        level: The logging level (string or int).
        filename: If provided, a FileHandler will be added for all logs.
        error_filename: If provided, a FileHandler will be added for error logs.
        fmt: The log message format.
        debug_fmt: The debug log message format.
        datefmt: The date/time format in log messages.
        debug_datefmt: The date/time format for debug log messages.
        handlers: Additional handlers to add.
        silence_loggers: Loggers to silence by setting their level to NOTSET.
        add_stream_handler: Whether to add a StreamHandler to output logs to console.

    """
    if isinstance(level, str):
        level = level.upper()
        if level not in valid_log_levels:
            raise ValueError(
                f"Invalid log level: {level}. Must be one of: {valid_log_levels}"
            )
        level = getattr(logging, level)
    elif isinstance(level, int):
        if level not in [getattr(logging, lvl) for lvl in valid_log_levels]:
            raise ValueError(f"Invalid numeric log level: {level}")
    else:
        raise TypeError(
            f"Invalid type for log level: {type(level)}. Must be str or int."
        )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    fmt = debug_fmt if level == logging.DEBUG else fmt
    datefmt = debug_datefmt if level == logging.DEBUG else datefmt

    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    ## Clear any existing handlers
    root_logger.handlers.clear()

    if filename:
        try:
            if use_rotating_handler:
                file_handler = get_rotating_file_handler(filename)
            else:
                file_handler = logging.FileHandler(filename)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as exc:
            root_logger.error(f"Failed adding file logging handler. Details: {exc}")

    if error_filename:
        try:
            if use_rotating_handler:
                error_file_handler = get_timed_rotating_file_handler(error_filename)
            else:
                error_file_handler = logging.FileHandler(error_filename)
            error_file_handler.setLevel(logging.ERROR)
            error_file_handler.setFormatter(formatter)
            root_logger.addHandler(error_file_handler)
        except Exception as exc:
            root_logger.error(
                f"Failed adding error file logging handler. Details: {exc}"
            )

    if add_stream_handler:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)

    if handlers:
        for handler in handlers:
            handler.setFormatter(formatter)
            root_logger.addHandler(handler)

    if silence_loggers:
        for logger_name in silence_loggers:
            _logger = logging.getLogger(logger_name)
            # _logger.setLevel(logging.NOTSET)
            _logger.propagate = False

    ## Log the configuration for debugging purposes
    root_logger.debug(f"Logging configured with level: {logging.getLevelName(level)}")
    if filename:
        root_logger.debug(f"Logging to file: {filename}")
    if error_filename:
        root_logger.debug(f"Logging errors to file: {error_filename}")