from bs4 import BeautifulSoup as Soup
from datasette import hookimpl
import sqlite3
from markupsafe import Markup

escaper = sqlite3.connect(":memory:")


def _quote(s):
    return escaper.execute("select quote(?)", [s]).fetchone()[0]


def build_directory_sql(q, table, count=False):
    wheres = " and ".join(
        "(name || ' ' || description || ' ' || extra_search) like '%' || {} || '%'".format(
            _quote(word.strip())
        )
        for word in q.split()
    )
    return "select {} from {} where {}".format(
        "count(*)" if count else "*", table, wheres
    )


def adjust_header_hierarchy(html, max_heading_level):
    soup = Soup("<html><body>{}</body></html>".format(html), "html5lib")
    headings = soup.select("h1,h2,h3,h4,h5,h6")
    if not headings:
        return html
    highest_level_in_html = int(min(h.name.lower() for h in headings)[-1])
    print(
        "max_heading_level = {}, highest_level_in_html = {}".format(
            max_heading_level, highest_level_in_html
        )
    )
    if highest_level_in_html >= max_heading_level:
        return html
    # Adjust all headers to fit the levels
    for heading in headings:
        heading_level = int(heading.name[-1])
        new_level = min(6, max_heading_level + (heading_level - highest_level_in_html))
        heading.name = "h{}".format(new_level)
    rendered = str(soup)
    # Strip the <body> / <head> / <html> wrappers
    return Markup(
        rendered.replace("<body>", "")
        .replace("</body>", "")
        .replace("<html>", "")
        .replace("</html>", "")
        .replace("<head>", "")
        .replace("</head>", "")
        .strip()
    )


@hookimpl
def extra_template_vars(request):
    return {
        "args": request.args,
        "path": request.path,
        "build_directory_sql": build_directory_sql,
        "build_directory_sql_count": lambda q, table: build_directory_sql(
            q, table, True
        ),
        "adjust_header_hierarchy": adjust_header_hierarchy,
    }
