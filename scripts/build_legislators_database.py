import pathlib
import sys

import sqlite_utils
import yaml


# Based on simonw/congress-legislators-datasette/build_database.py.
def flatten(dictionary):
    for key, value in dictionary.items():
        if isinstance(value, dict):
            for nested_key, nested_value in flatten(value):
                yield "{}_{}".format(key, nested_key), nested_value
        else:
            yield key, value


def add_legislators(db, root):
    for table_name in ("legislator_terms", "legislators"):
        db[table_name].drop(ignore=True)

    for filename in ("legislators-historical.yaml", "legislators-current.yaml"):
        data = yaml.safe_load((root / filename).read_text())
        for item in data:
            terms = item.pop("terms")
            flattened = dict(flatten(item))
            flattened["id"] = flattened["id_bioguide"]
            flattened["name"] = "{} {}".format(
                flattened["name_first"], flattened["name_last"]
            )
            pk = (
                db["legislators"]
                .insert(
                    flattened,
                    alter=True,
                    pk="id",
                    column_order=("id", "name"),
                )
                .last_pk
            )
            for term in terms:
                term["legislator_id"] = pk
            db["legislator_terms"].insert_all(
                terms,
                alter=True,
                foreign_keys=(("legislator_id", "legislators", "id"),),
                column_order=("legislator_id", "type", "state"),
            )


def add_district_offices(db, root):
    db["offices"].drop(ignore=True)
    offices = yaml.safe_load((root / "legislators-district-offices.yaml").read_text())
    for legislator in offices:
        legislator_id = legislator["id"]["bioguide"]
        for office in legislator["offices"]:
            office["legislator_id"] = legislator_id
        db["offices"].insert_all(
            legislator["offices"],
            pk="id",
            column_order=("id", "legislator_id"),
            alter=True,
            foreign_keys=(("legislator_id", "legislators", "id"),),
        )


def add_social_media(db, root):
    db["social_media"].drop(ignore=True)
    socials = yaml.safe_load((root / "legislators-social-media.yaml").read_text())

    def fixed_socials():
        for social in socials:
            social_media = social["social"]
            social_media["id"] = social["id"]["bioguide"]
            social_media["legislator_id"] = social["id"]["bioguide"]
            yield social_media

    db["social_media"].insert_all(
        fixed_socials(),
        pk="id",
        alter=True,
        foreign_keys=(("legislator_id", "legislators", "id"),),
        column_order=("id", "legislator_id"),
    )


def add_executives(db, root):
    for table_name in ("executives", "executive_terms"):
        db[table_name].drop(ignore=True)

    data = yaml.safe_load((root / "executive.yaml").read_text())
    for item in data:
        terms = item.pop("terms")
        flattened = dict(flatten(item))
        flattened["name"] = "{} {}".format(
            flattened["name_first"], flattened["name_last"]
        )
        pk = (
            db["executives"]
            .insert(
                flattened,
                alter=True,
                pk="id",
                column_order=("id", "name"),
            )
            .last_pk
        )
        for term in terms:
            term["executive_id"] = pk
        db["executive_terms"].insert_all(
            terms,
            alter=True,
            foreign_keys=(("executive_id", "executives", "id"),),
        )


def build_database(db_file, congress_legislators_path):
    db_path = pathlib.Path(db_file)
    root = pathlib.Path(congress_legislators_path)
    if not root.exists() or not root.is_dir():
        raise ValueError("{} is not a directory".format(root))
    if db_path.exists():
        db_path.unlink()
    db = sqlite_utils.Database(db_path)
    add_legislators(db, root)
    add_district_offices(db, root)
    add_social_media(db, root)
    add_executives(db, root)
    db.conn.execute("vacuum")


def main(args):
    if len(args) != 2 or not args[0].endswith(".db"):
        print(
            "Usage: python scripts/build_legislators_database.py "
            "legislators.db ../path/to/congress-legislators"
        )
        return 1
    build_database(args[0], args[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
