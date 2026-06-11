import html
import re
import sqlite3
import sys
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

TUTORIAL_FILES = sorted(Path("templates/pages/tutorials").glob("*.html")) + [
    Path("templates/pages/examples.html")
]
PLACEHOLDER_RE = re.compile(r":([A-Za-z_][A-Za-z0-9_]*)")
URL_STARTS = (
    "(https://datasette.io/legislators",
    "(https://datasette.io/legislators.json",
)
IGNORED_QUERY_PARAMS = {
    "_facet",
    "_facet_size",
    "_labels",
    "_next",
    "_shape",
    "_size",
    "_sort",
    "_hide_sql",
}


def markdown_urls(text):
    starts = []
    for prefix in URL_STARTS:
        pos = 0
        while True:
            index = text.find(prefix, pos)
            if index == -1:
                break
            starts.append(index)
            pos = index + len(prefix)

    for index in sorted(starts):
        depth = 1
        end = index + 1
        while end < len(text):
            char = text[end]
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    break
            end += 1
        yield html.unescape(text[index + 1 : end]), index + 1


def bind_parameters(sql, params):
    bindings = {
        key: values[-1]
        for key, values in params.items()
        if key not in {"sql", "_shape", "_hide_sql"}
    }
    for name in PLACEHOLDER_RE.findall(sql):
        bindings.setdefault(name, "")
    return bindings


def is_expected_sql_error(sql):
    # The learn-sql tutorial deliberately links to this query to show the
    # syntax error caused by a trailing comma before "from".
    return "family,\r\nfrom" in sql or "family,\nfrom" in sql


def validate_sql_link(conn, path, line, sql, params):
    expected_error = is_expected_sql_error(sql)
    try:
        rows = list(conn.execute(sql, bind_parameters(sql, params)))
    except Exception as ex:
        if expected_error:
            print(f"EXPECTED ERROR {path}:{line}: {ex}")
            return True
        print(f"FAIL {path}:{line}: {ex}")
        return False
    if expected_error:
        print(f"FAIL {path}:{line}: expected a syntax error, query succeeded")
        return False
    print(f"OK {path}:{line}: SQL returned {len(rows)} rows")
    return True


def where_clause_for_params(params):
    clauses = []
    values = []
    for key, param_values in params.items():
        if key in IGNORED_QUERY_PARAMS or key.startswith("_"):
            continue
        value = param_values[-1]
        if key.endswith("__exact"):
            column = key[: -len("__exact")]
            clauses.append(f'"{column}" = ?')
            values.append(value)
        elif key.endswith("__contains"):
            column = key[: -len("__contains")]
            clauses.append(f'"{column}" like ?')
            values.append(f"%{value}%")
        elif key.endswith("__startswith"):
            column = key[: -len("__startswith")]
            clauses.append(f'"{column}" like ?')
            values.append(f"{value}%")
        elif key.endswith("__in"):
            column = key[: -len("__in")]
            in_values = [item for item in value.split(",") if item]
            placeholders = ", ".join("?" for _ in in_values)
            clauses.append(f'"{column}" in ({placeholders})')
            values.extend(in_values)
        else:
            clauses.append(f'"{key}" = ?')
            values.append(value)
    if not clauses:
        return "", values
    return " where " + " and ".join(clauses), values


def validate_table_link(conn, path, line, parsed, params):
    bits = [unquote(bit) for bit in parsed.path.strip("/").split("/")]
    if len(bits) < 2:
        return True
    table = bits[1].removesuffix(".json")
    if table.endswith(".db"):
        return True
    if len(bits) >= 3:
        row_id = bits[2].removesuffix(".json")
        rows = list(conn.execute(f'select 1 from "{table}" where id = ?', (row_id,)))
        if rows:
            print(f"OK {path}:{line}: row link {table}/{row_id} exists")
            return True
        print(f"FAIL {path}:{line}: row link {table}/{row_id} returned no rows")
        return False

    where_clause, values = where_clause_for_params(params)
    rows = list(conn.execute(f'select count(*) from "{table}"{where_clause}', values))
    count = rows[0][0]
    if count:
        print(f"OK {path}:{line}: table link {table} returned {count} rows")
        return True
    print(f"FAIL {path}:{line}: table link {table} returned no rows")
    return False


def validate(db_path):
    conn = sqlite3.connect(db_path)
    seen = set()
    failures = 0
    checked = 0
    for path in TUTORIAL_FILES:
        text = path.read_text()
        for url, position in markdown_urls(text):
            if url in seen:
                continue
            seen.add(url)
            parsed = urlparse(url)
            params = parse_qs(parsed.query, keep_blank_values=True)
            line = text.count("\n", 0, position) + 1
            if "sql" in params:
                checked += 1
                if not validate_sql_link(conn, path, line, params["sql"][0], params):
                    failures += 1
            elif parsed.path.startswith("/legislators/"):
                checked += 1
                if not validate_table_link(conn, path, line, parsed, params):
                    failures += 1
    print(f"Checked {checked} legislators tutorial links")
    return failures == 0


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "legislators.db"
    raise SystemExit(0 if validate(db_path) else 1)
