import asyncio
from bs4 import BeautifulSoup as Soup
from datasette.app import Datasette
import pathlib
import sqlite_utils


async def main():
    db = sqlite_utils.Database("content.db")
    db["tutorials"].create(
        {
            "path": str,
            "title": str,
            "body": str,
        },
        pk="path",
        if_not_exists=True,
    )
    ds = Datasette(config_dir=pathlib.Path("."))
    index_response = await ds.client.get("/tutorials")
    index_soup = Soup(index_response.text, "html5lib")
    tutorial_links = index_soup.select(".content ul a")
    for link in tutorial_links:
        if not link["href"].startswith("/tutorials"):
            continue
        tutorial_response = await ds.client.get(link["href"])
        assert tutorial_response.status_code == 200
        soup = Soup(tutorial_response.text, "html5lib")
        title = soup.select("h1")[0].text
        # Remove any no-search elements
        for el in soup.select(".no-search"):
            el.decompose()
        body = soup.select(".content")[0].text
        db["tutorials"].insert(
            {
                "path": link["href"],
                "title": title,
                "body": body.strip(),
            },
            pk="path",
            replace=True,
        )


if __name__ == "__main__":
    asyncio.run(main())
