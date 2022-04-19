---
title: Datasette for search
summary: Datasette uses SQLite's built-in full-text search feature to provide faceted search over any correctly configured collection of records.
order: 5
---

Datasette is built on top of [SQLite](https://sqlite.org/), which includes a robust, full-featured [full-text search](https://www.sqlite.org/fts5.html) implementation.

Datasette automatically detects tables which have been configured for full-text search and adds a search box which can be used by human site users or accessed from the JSON or CSV APIs.

You can try this out now by [searching FARA records](https://fara.datasettes.com/) or [global power plants](https://global-power-plants.datasettes.com/global-power-plants/global-power-plants).

## Implementing search

The [sqlite-utils command-line tool](https://sqlite-utils.datasette.io/en/stable/cli.html#configuring-full-text-search) can be used to enable full-text search on a specific set of columns for a table:

    % sqlite-utils enable-fts mydb.db documents title summary

You can configure search directly within the Datasette interface by installing the [datasette-configure-fts](https://github.com/simonw/datasette-configure-fts) plugin.

[Fast Autocomplete Search for Your Website](https://simonwillison.net/2018/Dec/19/fast-autocomplete-search/) is a tutorial that shows how to write a scraper that populates a full-text search index in Datasette, then build a JavaScript autocomplete search interface using the Datasette JSON API.
