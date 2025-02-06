from datasette import hookimpl
from datasette.utils.asgi import Response

DID = "did:plc:5g7clyhlnvsbisbps3h7nvtr"


@hookimpl
def register_routes():
    return [
        ("^/\.well-known/atproto-did$", lambda: Response.text(DID)),
    ]
