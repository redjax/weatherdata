from __future__ import annotations

from settings.app_settings import APP_SETTINGS
from settings.celery_settings import CELERY_SETTINGS
from settings.db_settings import DB_SETTINGS
from settings.dramatiq_settings import DRAMATIQ_SETTINGS
from settings.logging_settings import LOGGING_SETTINGS
from settings.weatherapi_settings import WEATHERAPI_SETTINGS

## Set the name of a settings object to debug it, or 'all' to debug all settings objects.
#  i.e. "app" = APP_SETTINGS
DEBUG_SESSION = "all"
VALID_SESSIONS: list[str] = ["all", "app", "celery", "db", "logging", "dramatiq", "weatherapi", "dramatiq"]

def debug_app_settings(app_settings=APP_SETTINGS):
    print(f"app_settings: {app_settings.as_dict()}")
    return

def debug_celery_settings(celery_settings=CELERY_SETTINGS):
    print(f"celery_settings: {celery_settings.as_dict()}")
    return

def debug_db_settings(db_settings=DB_SETTINGS):
    print(f"db_settings: {db_settings.as_dict()}")
    return

def debug_logging_settings(logging_settings=LOGGING_SETTINGS):
    print(f"logging_settings: {logging_settings.as_dict()}")
    return        

def debug_dramatiq_settings(dramatiq_settings=DRAMATIQ_SETTINGS):
    print(f"dramatiq_settings: {dramatiq_settings.as_dict()}")
    return

def debug_weatherapi_settings(weatherapi_settings=WEATHERAPI_SETTINGS):
    print(f"weatherapi_settings: {weatherapi_settings.as_dict()}")
    return

def main(session: str):
    debug_sessions = {"app": debug_app_settings, "celery": debug_celery_settings, "db": debug_db_settings, "logging": debug_logging_settings, "dramatiq": debug_dramatiq_settings, "weatherapi": debug_weatherapi_settings}
    
    if session.lower()  not in VALID_SESSIONS:
        print(f"Invalid debug session: {session}")
        exit(1)

    if session == "all":
        print("Running all debuggers")
        
        for k, v in debug_sessions.items():
            print(f"\nRunning '{k}' debugger")
            v()
    
    else:
        print(f"Running debug session: {session}")
    
        match session.lower():
            case "app":
                debug_app_settings()
            case "celery":
                debug_celery_settings()
            case "db":
                debug_db_settings()
            case "logging":
                debug_logging_settings()
            case "dramatiq":
                debug_dramatiq_settings()
            case "weatherapi":
                debug_weatherapi_settings()
    

if __name__ == "__main__":
    main(session=DEBUG_SESSION)