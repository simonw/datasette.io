from datasette import hookimpl, Response

GLOBAL_POWER_PLANTS_URL = "https://datasette.io/global-power-plants/global-power-plants"


def redirect_global_power_plants(request):
    url = GLOBAL_POWER_PLANTS_URL
    if request.query_string:
        url = "{}?{}".format(url, request.query_string)
    return Response.redirect(url, status=301)


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
        (
            r"^/discord-llm/?$",
            lambda request: Response.redirect(
                "https://discord.gg/RKAH4b8TvE", status=301
            ),
        ),
        (
            r"^/discord-enrichments/?$",
            lambda request: Response.redirect(
                "https://discord.gg/tcTpMVQdRc", status=301
            ),
        ),
        (
            r"^/global-power-plants\*/global-power-plants/?$",
            redirect_global_power_plants,
        ),
        # /help/X may be linked to from the datasette CLI - served with 302 because I may change
        # what they target in the future.
        (
            r"^/help/extensions/?$",
            lambda request: Response.redirect(
                "https://docs.datasette.io/en/stable/installation.html#a-note-about-extensions",
                status=302,
            ),
        ),
    )
