from __future__ import annotations

import typing as t
import sys

from loguru import logger as log
from setup import setup_loguru_logging

from cyclopts import App, Group, Parameter

from loguru import logger as log

from .weather import weather_app

app = App(name="weathercli", help="CLI for WeatherData app.")

app.meta.group_parameters = Group("Session Parameters", sort_key=0)

## Mount apps
app.command(weather_app)

@app.meta.default
def cli_launcher(*tokens: t.Annotated[str, Parameter(show=False, allow_leading_hyphen=True)], debug: bool = False):
    log.remove(0)
    
    if debug:
        log.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss} | [{level}] | {name}.{function}:{line} |> {message}", level="DEBUG")
        
        log.debug("CLI debugging enabled.")
    else:
        log.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss} [{level}] : {message}", level="INFO")
                
    app(tokens)

if __name__ == "__main__":
    app()