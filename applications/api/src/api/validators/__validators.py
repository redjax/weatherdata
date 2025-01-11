from __future__ import annotations

from loguru import logger as log

from typing import Optional, Type, Union

from fastapi import APIRouter


def is_str(input: str = None) -> str:
    if not input:
        raise ValueError("Missing input to evaluate")

    if not isinstance(input, str):
        try:
            input: str = str(input)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception convering input from type({type(input)}) to type(str). Details: {exc}"
            )
            log.error(msg)

            raise exc

    return input


def is_list_str(_list: list[str] = None) -> list[str]:
    if not _list:
        raise ValueError("Missing input list to evaluate")

    if not isinstance(_list, list):
        raise ValueError("Input list must be of type list")

    for _i in _list:
        if not isinstance(_i, str):
            raise ValueError(
                f"Non-str list item ({type(_i)}): {_i}. List items must be of type str"
            )

    return _list


def validate_root_path(root_path: str = None) -> str:
    if not root_path:
        raise ValueError("Missing root_path value")

    if not isinstance(root_path, str):
        try:
            root_path: str = str(root_path)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception convering root_path from type({type(root_path)}) to type(str)"
            )
            log.error(msg)

            raise exc

    return root_path


def validate_openapi_tags(_tags: list[dict] = None) -> list[dict]:
    if not _tags:
        raise ValueError("Missing list of tag dicts to evaluate")

    if not isinstance(_tags, list):
        raise ValueError("Input object must be of type list")

    for _i in _tags:
        if not isinstance(_i, dict):
            raise ValueError(
                f"Non-dict list item ({type(_i)}): {_i}. List items must be of type dict"
            )

    return _tags


def validate_router(router: APIRouter = None, none_ok: bool = False) -> APIRouter:
    if not router:
        if not none_ok:
            raise ValueError("Missing APIRouter to evaluate")

    if not isinstance(router, APIRouter):
        raise TypeError(
            f"Invalid router type: {type(router)}. Must be of type(APIRouter)"
        )

    return router