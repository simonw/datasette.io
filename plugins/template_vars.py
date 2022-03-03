from datasette import hookimpl
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


@hookimpl
def extra_template_vars(request):
    return {
        "args": request.args,
        "path": request.path,
        "build_directory_sql": build_directory_sql,
        "build_directory_sql_count": lambda q, table: build_directory_sql(
            q, table, True
        ),
    }
