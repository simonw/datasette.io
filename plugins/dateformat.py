from datasette import hookimpl
import datetime


def suffix(d):
    return "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")


def prettydate(date):
    if isinstance(date, str):
        date = datetime.date.fromisoformat(date)
    return "{day}{suffix} {month} {year}".format(
        day=date.day,
        month=date.strftime("%B"),
        suffix=suffix(date.day),
        year=date.year,
    )


@hookimpl
def extra_template_vars():
    return {"prettydate": prettydate}
