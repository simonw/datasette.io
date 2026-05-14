import re

from plugins.redirects import register_routes


class Request:
    def __init__(self, query_string=""):
        self.query_string = query_string


def test_global_power_plants_stray_asterisk_redirect():
    path = "/global-power-plants*/global-power-plants"
    matches = [view for regex, view in register_routes() if re.match(regex, path)]

    assert len(matches) == 1
    response = matches[0](Request())
    assert response.status == 301
    assert (
        response.headers["Location"]
        == "https://datasette.io/global-power-plants/global-power-plants"
    )


def test_global_power_plants_stray_asterisk_redirect_preserves_query_string():
    path = "/global-power-plants*/global-power-plants"
    matches = [view for regex, view in register_routes() if re.match(regex, path)]

    assert len(matches) == 1
    response = matches[0](Request("_facet=owner&_sort=name&owner=Example"))
    assert response.status == 301
    assert (
        response.headers["Location"]
        == "https://datasette.io/global-power-plants/global-power-plants"
        "?_facet=owner&_sort=name&owner=Example"
    )


def test_global_power_plants_stray_asterisk_redirect_is_literal():
    path = "/global-power-plantsx/global-power-plants"

    assert not any(re.match(regex, path) for regex, view in register_routes())
