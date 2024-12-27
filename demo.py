from __future__ import annotations

from domain.exc import FileProcessingError
from http_lib import (
    HttpxController,
    build_request,
    client,
    get_http_controller,
    merge_headers,
)
import httpx

if __name__ == "__main__":
    req = build_request(url="https://www.google.com")
    
    with get_http_controller() as http_ctl:
        res = http_ctl.client.send(req)
        print(f"[{res.status_code}: {res.reason_phrase}]")