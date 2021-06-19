from bs4 import BeautifulSoup as Soup
from datasette import hookimpl
import jinja2
import sqlite3

escaper = sqlite3.connect(":memory:")


def _quote(s):
    return escaper.execute("select quote(?)", [s]).fetchone()[0]


def build_directory_sql(q, table, count=False):
    wheres = " and ".join(
        "(name || ' ' || description) like '%' || {} || '%'".format(
            _quote(word.strip())
        )
        for word in q.split()
    )
    return "select {} from {} where {}".format(
        "count(*)" if count else "*", table, wheres
    )


def remove_links_inside_pre(html):
    soup = Soup("<html><body>{}</body></html>".format(html), "html5lib")
    for pre in soup.findAll("pre"):
        for a in pre.findAll("a"):
            a.replace_with(a.text)
    rendered = str(soup)
    # Strip the <body> and </body>
    return jinja2.Markup(
        rendered.replace("<body>", "")
        .replace("</body>", "")
        .replace("<html>", "")
        .replace("</html>", "")
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
        "remove_links_inside_pre": remove_links_inside_pre,
    }
