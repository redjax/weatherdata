import typing as t

from fastapi.responses import Response

API_RESPONSE_DICT: dict[int, dict[str, t.Any]] = {404: {"description": "Not found"}, 500: {"description": "Internal server error"}}


def img_response(img_bytes: bytes, media_type: str = "image") -> Response:
    if not img_bytes:
        raise ValueError("img_bytes cannot be None.")
    if not isinstance(img_bytes, bytes):
        raise TypeError(f"Invalid type for img_bytes: {type(img_bytes)}. Must be a bytes object.")
    
    res: Response = Response(
        content=img_bytes,
        media_type=media_type
    )
    
    return res
