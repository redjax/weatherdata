from loguru import logger as log
import setup
import db
import depends
import settings

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"))
    
    try:
        setup.setup_database()
        log.success("Database initialized.")
    except Exception as exc:
        msg = f"({type(exc)}) Error initializing database. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    