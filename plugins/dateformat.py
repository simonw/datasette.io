from datasette import hookimpl
from dateutil import parser


def suffix(d):
    return "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")


def prettydate(date):
    if isinstance(date, str):
        try:
            date = parser.parse(date)
        except parser.ParserError:
            return date
    return "{day}{suffix} {month} {year}".format(
        day=date.day,
        month=date.strftime("%B"),
        suffix=suffix(date.day),
        year=date.year,
    )


@hookimpl
def extra_template_vars():
    return {"prettydate": prettydate}
