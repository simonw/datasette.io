from datasette import hookimpl, Response


@hookimpl
def register_routes():
    return (
        (
            r"^/conduct/?$",
            lambda request: Response.redirect(
                "https://github.com/simonw/datasette/blob/main/CODE_OF_CONDUCT.md",
                status=301,
            ),
        ),
        (
            r"^/discord/?$",
            lambda request: Response.redirect(
                "https://discord.gg/ktd74dm5mw", status=301
            ),
        ),
    )
