from __future__ import annotations

import dramatiq
import http_lib
import httpx
from loguru import logger as log

@dramatiq.actor
def count_words(url):
    res = httpx.get(url)
    
    count = len(res.text.split(" "))
    log.info(f"There are {count} words at {url!r}")
