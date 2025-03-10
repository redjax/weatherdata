from __future__ import annotations

import logging
import random
import typing as t

log = logging.getLogger(__name__)

__all__ = ["get_random_item", "get_random_index", "shuffle_list"]

def shuffle_list(list_: t.List[t.Any]) -> t.List[t.Any]:
    return random.sample(list_, len(list_))


def get_random_item(list_: t.List[t.Any]) -> t.Any:
    return random.choice(list_)


def get_random_index(list_: t.List[t.Any]) -> int:
    return random.randint(0, len(list_) - 1)