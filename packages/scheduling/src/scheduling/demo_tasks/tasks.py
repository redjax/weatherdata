from loguru import logger as log

import http_lib
import httpx
import dramatiq


@dramatiq.actor
def count_words(url):
    res = httpx.get(url)
    
    count = len(res.text.split(" "))
    log.info(f"There are {count} words at {url!r}")
