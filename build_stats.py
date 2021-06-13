import click
import json
import sqlite_utils


@click.command()
@click.argument(
    "db_filename",
    type=click.Path(file_okay=True, dir_okay=False),
)
@click.argument(
    "stats_file",
    type=click.File(),
)
def cli(db_filename, stats_file):
    db = sqlite_utils.Database(db_filename)
    stats = json.load(stats_file)
    for package, days in stats.items():
        for date, downloads in days.items():
            db["stats"].insert(
                {
                    "package": package,
                    "date": date,
                    "downloads": downloads,
                },
                pk=("package", "date"),
                replace=True,
            )


if __name__ == "__main__":
    cli()
