from datetime import date, datetime
from pathlib import Path
import re

from bs4 import BeautifulSoup as Soup
import markdown
import sqlite_utils
import yaml

BLOG_DIR = Path("blog-content")
DB_PATH = "content.db"


def split_front_matter(text, path):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            metadata = yaml.safe_load("\n".join(lines[1:index])) or {}
            body = "\n".join(lines[index + 1 :]).lstrip()
            return metadata, body

    raise ValueError("{} starts with front matter but does not close it".format(path))


def as_string(value):
    if isinstance(value, datetime):
        return value.isoformat(sep=" ")
    if isinstance(value, date):
        return value.isoformat()
    if value is None:
        return None
    return str(value)


def year_from_datetime_utc(value):
    text = as_string(value)
    if not text:
        return None
    return text[:4]


def summary_from_html(html):
    soup = Soup(html, "html5lib")
    paragraph = soup.find("p")
    if paragraph:
        text = paragraph.get_text(" ", strip=True)
    else:
        text = soup.get_text(" ", strip=True)
    return re.sub(r"\s+([,.;:!?])", r"\1", text)


def parse_blog_post(path):
    text = path.read_text(encoding="utf-8")
    metadata, body = split_front_matter(text, path)
    title = as_string(metadata.get("title"))
    datetime_utc_value = metadata.get("datetime_utc")
    datetime_utc = as_string(datetime_utc_value)
    year = year_from_datetime_utc(datetime_utc_value)
    slug = as_string(metadata.get("slug")) or path.stem
    author = as_string(metadata.get("author"))
    author_url = as_string(metadata.get("author_url"))

    if not title:
        raise ValueError("{} is missing title in front matter".format(path))
    if not datetime_utc:
        raise ValueError("{} is missing datetime_utc in front matter".format(path))
    if not year:
        raise ValueError("{} has an invalid datetime_utc value".format(path))
    if not author:
        raise ValueError("{} is missing author in front matter".format(path))

    html = markdown.markdown(body, extensions=["extra"])
    return {
        "path": "/blog/{}/{}/".format(year, slug),
        "year": year,
        "slug": slug,
        "source_path": str(path),
        "title": title,
        "datetime_utc": datetime_utc,
        "author": author,
        "author_url": author_url,
        "body": body,
        "html": html,
        "summary": summary_from_html(html),
    }


def load_blog_posts(db_path=DB_PATH, blog_dir=BLOG_DIR):
    blog_dir = Path(blog_dir)
    if not blog_dir.exists():
        raise ValueError("{} does not exist".format(blog_dir))

    rows = [parse_blog_post(path) for path in sorted(blog_dir.glob("*.md"))]
    paths = [row["path"] for row in rows]
    if len(paths) != len(set(paths)):
        raise ValueError("Duplicate blog post paths found")

    db = sqlite_utils.Database(db_path)
    columns = {
        "path": str,
        "year": str,
        "slug": str,
        "source_path": str,
        "title": str,
        "datetime_utc": str,
        "author": str,
        "author_url": str,
        "body": str,
        "html": str,
        "summary": str,
    }
    table = db["blog_posts"]
    table.create(
        columns,
        pk="path",
        if_not_exists=True,
    )
    existing_columns = table.columns_dict.keys()
    for column, type_ in columns.items():
        if column not in existing_columns:
            table.add_column(column, type_)
    with db.conn:
        db.conn.execute("delete from blog_posts")
        if rows:
            table.insert_all(rows, pk="path", replace=True)
    table.create_index(["datetime_utc"], if_not_exists=True)
    table.create_index(["slug"], if_not_exists=True)
    return rows


if __name__ == "__main__":
    load_blog_posts()
