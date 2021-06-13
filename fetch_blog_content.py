import click
import feedparser
import httpx
import sqlite_utils
import urllib


def all_entries(url):
    while url:
        response = httpx.get(url, timeout=30)
        entries = feedparser.parse(response.text)["entries"]
        yield from (
            {
                "id": entry["id"],
                "title": entry["title"],
                "published": entry["published"],
                "url": entry["link"].split("#")[0],
                "body": entry["summary"],
                "tags": [t["term"] for t in entry["tags"]],
            }
            for entry in entries
        )
        next_url = response.links.get("next", {}).get("url")
        if next_url:
            url = urllib.parse.urljoin(url, next_url)
        else:
            break


@click.command()
@click.argument(
    "db_filename",
    type=click.Path(file_okay=True, dir_okay=False),
)
@click.argument("tags", type=str, nargs=-1)
@click.option(
    "--refresh",
    is_flag=True,
    help="Pull everything rather than stopping at first already-seen item",
)
def cli(db_filename, tags, refresh):
    db = sqlite_utils.Database(db_filename)
    if refresh:
        seen_ids = set()
        db["entries"].drop()
    else:
        seen_ids = {row["id"] for row in db["entries"].rows}

    for tag in tags:
        for entry in all_entries("https://simonwillison.net/tags/{}.atom".format(tag)):
            if entry["id"] in seen_ids:
                break
            db["entries"].insert(entry, pk="id", replace=True)


if __name__ == "__main__":
    cli()
