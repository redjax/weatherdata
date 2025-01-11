import typing as t
from loguru import logger as log

from api.tag_definitions import tags_metadata
from api.validators import validate_openapi_tags, validate_router, is_str
from api.constants import default_openapi_url, default_allow_credentials, default_allowed_headers, default_allowed_methods,  default_allowed_origins

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

def fix_api_docs(app: FastAPI = None):
    """Fix error loading /docs when a root_path is set.

    Call after declaring an app with a root_path set, for example:
        app = FastAPI(root_path="/some/path")
        fix_api_docs(app)

    When a root_path is declared, the default /docs URL breaks, and returns
    an error:
        Fetch error
        Not Found /api/v1/openapi.json
    """
    if not app:
        raise ValueError("Missing a FastAPI app with a root_path var declared")

    if not isinstance(app, FastAPI):
        raise TypeError(
            f"Invalid type for FastAPI app: ({type(app)}). Value must be of type FastAPI."
        )

    @app.get(app.root_path + "/openapi.json", include_in_schema=False)
    def custom_swagger_ui_html():
        return app.openapi()
    
    
def update_tags_metadata(
    tags_metadata: list = tags_metadata,
    update_metadata: t.Union[list[dict[str, str]], dict[str, str]] = None,
):
    """Update the global tags_metadata list with new values.

    Import this function in another app, create a new list of tags (or
    a single tag dict, {"name": ..., "description": ...}), then pass both
    the imported tags_metadata and the new list/single instance of tag objects.

    This funciton will combine them into a new tags_metadata object
    """
    if not tags_metadata:
        raise ValueError("Missing value for tags_metadata")

    if not update_metadata:
        raise ValueError("Missing value for update_metadata")

    if isinstance(update_metadata, list):
        ## List of dicts was passed

        # print(f"[DEBUG] Detected list of new tags: {update_metadata}")

        tags_metadata = tags_metadata + update_metadata

        return_obj = tags_metadata

    elif isinstance(update_metadata, dict):
        ## Single tag dict was passed

        # print(f"[DEBUG] Detected single dict for new tag: {update_metadata}")

        tags_metadata.append(update_metadata)

        return_obj = tags_metadata

    else:
        raise ValueError(
            "Type of update_metadata must be one of list[dict[str,str]] or dict[str,str]"
        )

    return return_obj


def add_cors_middleware(
    app: FastAPI = None,
    cors: CORSMiddleware = CORSMiddleware,
    allow_credentials: bool = default_allow_credentials,
    allowed_origins: list[str] = default_allowed_origins,
    allowed_headers: list[str] = default_allowed_headers,
    allowed_methods: list[str] = default_allowed_methods,
) -> FastAPI:
    try:
        app.add_middleware(
            cors,
            allow_credentials=allow_credentials,
            allow_origins=allowed_origins,
            allow_methods=allowed_methods,
            allow_headers=allowed_headers,
        )

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception adding CORS middleware to FastAPI app. Details: {exc}"
        )
        log.error(msg)

        raise exc

    return app


def add_routers(app: FastAPI = None, routers: list[APIRouter] = None) -> FastAPI:
    if not app:
        raise ValueError("Missing FastAPI App()")

    if not routers:
        raise ValueError("Missing list of APIRouters to add to FastAPI app")

    if not isinstance(app, FastAPI):
        raise TypeError(f"Invalid type for app: ({type(app)}). Must be type(FastAPI)")

    if not isinstance(routers, list):
        raise TypeError(
            f"Invalid type for routers: ({type(routers)}). Must be type(list[APIRouter])"
        )

    for _i in routers:
        if not isinstance(_i, APIRouter):
            raise TypeError(
                f"Invalid type for router: ({type(_i)}). Must be type(APIRouter)"
            )

    for router in routers:
        app.include_router(router)

    return app


def get_app(
    debug: bool = False,
    cors: bool = True,
    root_path: str = "/",
    title: str = "DEFAULT_TITLE",
    description: str = "DEFAULT_DESCRIPTION",
    version: str = "0.0.0",
    openapi_url: str = default_openapi_url,
    openapi_tags: list = tags_metadata,
    routers: list[APIRouter] = None,
) -> FastAPI:
    """Generate a FastAPI app and return."""
    for _var in [root_path, title, description, version, openapi_url]:
        if _var:
            is_str(input=_var)
        else:
            continue

    validate_openapi_tags(openapi_tags)

    if routers:
        for r in routers:
            validate_router(r, none_ok=True)

    try:
        app: FastAPI = FastAPI(
            root_path=root_path,
            title=title,
            description=description,
            version=version,
            openapi_url=openapi_url,
            openapi_tags=openapi_tags,
            debug=debug,
        )

        if cors:
            add_cors_middleware(app=app)

        if routers:
            for router in routers:
                app.include_router(router)

    except Exception as exc:
        msg = Exception(f"Unhandled exception creating FastAPI App. Details: {exc}")
        log.error(msg)

        raise exc

    return app
