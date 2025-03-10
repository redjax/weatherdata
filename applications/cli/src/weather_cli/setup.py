from __future__ import annotations

from datetime import timedelta
import typing as t
from pathlib import Path
import shutil

from core_utils import time_utils
from cyclopts import App, Group, Parameter
from loguru import logger as log

setup_app = App(name="setup", help="CLI for project setup")


@setup_app.command(name="app-config-files")
def setup_config_files():
    config_toml_files: list[Path] = [p for p in Path("config").rglob("**/*.toml") if p.is_file()]
    log.debug(f"Found ({len(config_toml_files)}) TOML config file(s) in path 'config/'")
    
    successes: list[dict] = []
    failures: list[dict] = []
    
    for config_toml in config_toml_files:
        log.debug(f"Config .toml: {config_toml}")
        
        local_config_file = config_toml.with_stem(config_toml.stem + ".local")
        log.debug(f".local config: {local_config_file} (exists: {Path(local_config_file).exists()})")
        
        metadata = {"orig": config_toml, "copy": local_config_file}
        
        if not Path(local_config_file).exists():
            log.info(f"Creating .local config file: {local_config_file}")
            # Path(local_config_file).touch()
            try:
                shutil.copy2(src=config_toml, dst=local_config_file)
                log.info(f"Copied '{config_toml}' to '{local_config_file}'")

                successes.append(metadata)
            except Exception as exc:
                msg = f"({type(exc)}) Error copying '{config_toml}' to '{local_config_file}'. Details: {exc}"
                log.error(msg)
                
                failures.append(metadata)
                continue
        else:
            log.debug(f"Skip copying '{config_toml}' to '{local_config_file}', .local version already exists")
            continue
        
    log.info(f"Copied [{len(successes)}] config file(s) to .local version")
    if len(failures) > 0:
        log.warning(f"Failed to copy [{len(failures)}] config file(s) to .local version. Failures:\n{failures}")

@setup_app.command(name="direnv")
def setup_direnv():
    if not Path(".envrc").exists():
        log.warning(f"No .envrc file detected. Create one and re-run this command.")
        return
    
    if not Path(".direnv").exists():
        raise FileNotFoundError("Could not find direnv configs in path ./direnv.")
    
    successes = []
    failures = []
    existed = []
    
    for f in Path(".direnv").glob("**/*.example"):
        f_copy = Path(str(f).replace('.example', ''))
        log.debug(f"Copying example file: {f} to {f_copy}")
        
        metadata = {"orig": f, "copy": f_copy}
        
        if not f_copy.exists():
            try:
                shutil.copy2(src=f, dst=f_copy)
                log.debug(f"Copied {f} to {f_copy}")
                
                successes.append(metadata)
            except Exception as exc:
                msg = f"({type(exc)}) Error copying '{f}' to '{f_copy}'. Details: {exc}"
                log.error(msg)
                
                failures.append(metadata)
                
                continue
        else:
            log.debug(f"Skip copying '{f}' to '{f_copy}', .local version already exists")
            existed.append(metadata)
            continue
        
    log.info(f"Copied [{len(successes)}] config file(s) to .local version")
    log.debug(f"Successful copies: \n{successes}")
    
    if len(existed) > 0:
        log.info(f"({len(existed)}) config file(s) already existed and were not copied")
        log.debug(f"Files that were not copied:\n{existed}")

    if len(failures) > 0:
        log.warning(f"Failed to copy [{len(failures)}] config file(s) to .local version. Failures:\n{failures}")
    
    return
    