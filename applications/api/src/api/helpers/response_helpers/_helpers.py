from pathlib import Path
import typing as t

# from helpers import validators
from loguru import logger as log

def stream_file_contents(f_path: t.Union[str, Path] = None, mode: str = "rb"):
    if f_path is None:
        log.warning(ValueError("Missing a file path"))
        return None
    
    f_path: Path = Path(str(f_path)).expanduser() if "~" in f_path else Path(str(f_path))

    if not f_path.exists():
        log.error(f"Could not find  file: '{f_path}'.")
        raise FileNotFoundError(f"Could not find  file: '{f_path}'.")

    with open(f_path, mode=mode) as f_out:
        yield from f_out
