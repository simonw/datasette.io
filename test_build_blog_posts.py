import sqlite_utils

from build_blog_posts import load_blog_posts, parse_blog_post


def test_parse_blog_post(tmp_path):
    path = tmp_path / "hello-world.md"
    path.write_text("""---
title: Hello world
datetime_utc: 2026-05-13 20:58:56
author: Simon Willison
author_url: https://simonwillison.net
---

First **paragraph**.

Second paragraph.
""")

    post = parse_blog_post(path)

    assert post["path"] == "/blog/2026/hello-world/"
    assert post["year"] == "2026"
    assert post["slug"] == "hello-world"
    assert post["title"] == "Hello world"
    assert post["datetime_utc"] == "2026-05-13 20:58:56"
    assert post["author"] == "Simon Willison"
    assert post["author_url"] == "https://simonwillison.net"
    assert post["body"] == "First **paragraph**.\n\nSecond paragraph."
    assert "<strong>paragraph</strong>" in post["html"]
    assert post["summary"] == "First paragraph."


def test_load_blog_posts_replaces_existing_rows(tmp_path):
    blog_dir = tmp_path / "blog-content"
    blog_dir.mkdir()
    (blog_dir / "new-blog.md").write_text("""---
title: New blog
datetime_utc: 2026-05-13 20:58:56
author: Simon Willison
author_url: https://simonwillison.net
---

Post body.
""")
    db_path = tmp_path / "content.db"
    db = sqlite_utils.Database(db_path)
    db["blog_posts"].insert({"path": "/blog/old-post", "title": "Old"}, pk="path")

    load_blog_posts(db_path, blog_dir)

    rows = list(db["blog_posts"].rows)
    assert rows == [
        {
            "path": "/blog/2026/new-blog/",
            "year": "2026",
            "slug": "new-blog",
            "source_path": str(blog_dir / "new-blog.md"),
            "title": "New blog",
            "datetime_utc": "2026-05-13 20:58:56",
            "author": "Simon Willison",
            "author_url": "https://simonwillison.net",
            "body": "Post body.",
            "html": "<p>Post body.</p>",
            "summary": "Post body.",
        }
    ]
