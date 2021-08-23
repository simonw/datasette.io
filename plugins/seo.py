from datasette import hookimpl
from datasette.utils.asgi import Response

ROBOTS_TXT = """
Sitemap: https://datasette.io/sitemap.xml

User-agent: *
Disallow: /content
Disallow: /docs-index
Disallow: /dogsheep-index
Disallow: /blog
Disallow: /-/beta
""".strip()


@hookimpl
def register_routes():
    return [
        ("^/robots.txt$", robots_txt),
        ("^/sitemap.xml$", sitemap_xml),
    ]


def robots_txt():
    return Response.text(ROBOTS_TXT)


async def urls(datasette):
    paths = ["/", "/for", "/examples", "/plugins", "/tools", "/news"]
    db = datasette.get_database("content")
    for row in await db.execute("select _path from uses"):
        paths.append("/" + row["_path"].split(".")[0])
    for row in await db.execute("select name from plugins"):
        paths.append("/plugins/" + row["name"])
    for row in await db.execute("select name from tools"):
        paths.append("/tools/" + row["name"])
    return ("https://datasette.io{}".format(path) for path in paths)


async def sitemap_xml(datasette):
    content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in await urls(datasette):
        content.append("<url><loc>{}</loc></url>".format(url))
    content.append("</urlset>")
    return Response("\n".join(content), 200, content_type="application/xml")
