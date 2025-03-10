from __future__ import annotations

__all__ = ["PANDAS_DATETIME_FORMAT", "PANDAS_DATE_FORMAT", "PANDAS_TIME_FORMAT", "PANDAS_ENGINE"]

PANDAS_DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%SZ"
PANDAS_DATE_FORMAT: str = "%Y-%m-%d"
PANDAS_TIME_FORMAT: str = "%H:%M:%S"
PANDAS_ENGINE: str = "pyarrow"