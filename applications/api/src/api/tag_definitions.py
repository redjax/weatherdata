"""Add metadata to tags assigned throughout the app.

If a router/endpoint's tags match
any of these, the description and other metadata will be applied on the docs page.
   
This tags_metadata can be imported and extended with tags_metadata.append(new_tags_dict).
 
You can also create a new list of tags ([{"name": ..., "description": ...}, ...]) and join
them with tags_metadata = tags_metadata + new_tags_list
   
How to add new tags:
   
* Create a tag dict
* ex_tag = {"name": "example", "description": "An example tag"}
* Append to existing metadata object
* tags_metadata.append(garlic_metadata)
     
Do this operation early, preferable before even creating the FastAPI app object. Otherwise,
tags render really weird.
   
Do not declare tags on a submodule, like an APIRouter module for example. Appending tags
once the server is already running makes them unusable in the /docs site.
"""

from __future__ import annotations

## Default tags_metadata object.
tags_metadata = [
    {
        "name": "default",
        "description": "Tags have not been added to these endpoints/routers.",
    },
    {
        "name": "util",
        "description": "Utility functions, routes, & more. These utils are in the root of the app, and accessible by all sub-apps and routers.",
    },
]
