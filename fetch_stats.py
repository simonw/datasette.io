import httpx
import pathlib
import click
import json


@click.command()
@click.argument(
    "stats_file",
    type=click.Path(file_okay=True, dir_okay=False),
)
@click.argument("packages", nargs=-1)
def cli(stats_file, packages):
    path = pathlib.Path(stats_file)
    if path.exists():
        data = json.load(path.open())
    else:
        data = {}
    for package in packages:
        url = "https://pypistats.org/api/packages/{}/overall?mirrors=true".format(
            package
        )
        response = httpx.get(url)
        response.raise_for_status()
        raw_stats = response.json()["data"]
        # Re-arrange into date: number dictionary
        package_stats = {rs["date"]: rs["downloads"] for rs in raw_stats}
        # Combine that with the existing stats for this package
        data[package] = {**(data.get("package") or {}), **package_stats}
    path.write_text(json.dumps(data, indent=4, sort_keys=True))


if __name__ == "__main__":
    cli()
