from __future__ import annotations

from domain.exc import FileProcessingError
import setup
from core_utils import time_utils

from http_lib import (
    HttpxController,
    build_request,
    client,
    get_http_controller,
    merge_headers,
)
import httpx
from loguru import logger as log

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level="DEBUG")
    log.debug("Test debug log")
    
    ts = time_utils.get_ts(as_str=True, safe_str=True)
    log.debug(f"Example timestamp: {ts}")
    
    req = build_request(url="https://www.google.com")
    
    log.info("Making test request to google.com")
    with get_http_controller() as http_ctl:
        res: httpx.Response = http_ctl.client.send(req)
        print(f"[{res.status_code}: {res.reason_phrase}]")