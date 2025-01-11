from api.tag_definitions import tags_metadata

default_allow_credentials: bool = True
default_allowed_origins: list[str] = ["*"]
default_allowed_methods: list[str] = ["*"]
default_allowed_headers: list[str] = ["*"]

## Route to openapi docs. This returns the docs site as a JSON object
#  If you set this to the same route as docs (i.e. /docs), you will only
#  get the openapi JSON response, no Swagger docs.
default_openapi_url: str = "/docs/openapi"

default_api_str: str = "/api/v1"
