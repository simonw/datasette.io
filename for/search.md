---
title: Datasette for search
summary: Datasette uses SQLite's built-in full-text search feature to provide faceted search over any correctly configured collection of records.
order: 6
---

Datasette is built on top of [SQLite](https://sqlite.org/), which includes a robust, full-featured [full-text search](https://www.sqlite.org/fts5.html) implementation.

Datasette automatically detects tables which have been configured for full-text search and adds a search box which can be used by human site users or accessed from the JSON or CSV APIs.

You can try this out now by [searching FARA records](https://fara.datasettes.com/) or [global power plants](https://datasette.io/global-power-plants/global-power-plants).

## Enabling search for a table

The [sqlite-utils command-line tool](https://sqlite-utils.datasette.io/en/stable/cli.html#configuring-full-text-search) can be used to enable full-text search on a specific set of columns for a table:

    % sqlite-utils enable-fts mydb.db documents title summary

Alternatively, you can configure search directly within the Datasette interface by installing the [datasette-configure-fts](https://github.com/simonw/datasette-configure-fts) plugin.

[Fast Autocomplete Search for Your Website](https://simonwillison.net/2018/Dec/19/fast-autocomplete-search/) is a tutorial that shows how to write a scraper that populates a full-text search index in Datasette, then build a JavaScript autocomplete search interface using the Datasette JSON API.

## Implementing search with a canned query

Datasette [canned queries](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) can be used to configure a SQL query which returns search results for a table, ordered by relevance.

The search on [www.niche-museums.com](https://www.niche-museums.com/) uses this approach. Here's an example search, for `bones`:

- [www.niche-museums.com/browse/search?q=bones](https://www.niche-museums.com/browse/search?q=bones)

This uses the `search` canned query, which is [defined here]([https://github.com/simonw/til/blob/8f961be162868c53b5c484272091bdab703a747a/metadata.yaml#L16-L32](https://github.com/simonw/museums/blob/74e999c0e82781302bf0346a761ee5d88e168863/metadata.yaml#L55-L69)) and looks like this:

    select
      museums_fts.rank,
      museums.*
    from
      museums
      join museums_fts on museums.id = museums_fts.rowid
    where
      museums_fts match case
        :q
        when '' then '*'
        else escape_fts_query(:q)
      end
    order by
      museums_fts.rank

Try [that query here](https://www.niche-museums.com/browse?sql=select%0D%0A++museums_fts.rank%2C%0D%0A++museums.*%0D%0Afrom%0D%0A++museums%0D%0A++join+museums_fts+on+museums.id+%3D+museums_fts.rowid%0D%0Awhere%0D%0A++museums_fts+match+case%0D%0A++++%3Aq%0D%0A++++when+%27%27+then+%27*%27%0D%0A++++else+escape_fts_query%28%3Aq%29%0D%0A++end%0D%0Aorder+by%0D%0A++museums_fts.rank&q=bones).

The results are then rendered by [this custom template](https://github.com/simonw/museums/blob/74e999c0e82781302bf0346a761ee5d88e168863/templates/query-browse-search.html).

## Plugins for search

The **[datasette-search-all](https://datasette.io/plugins/datasette-search-all)** plugin adds a search box which runs searches in parallel against all of the FTS-configured tables in all of the databases attached to Datasette.

You can see that in action here: [fara.datasettes.com/-/search?q=manafort](https://fara.datasettes.com/-/search?q=manafort)

**[dogsheep-beta](https://datasette.io/plugins/dogsheep-beta)** is a plugin which adds a customizable search engine that can create an index to search multiple tables at once with combined relevance scoring. It is used for the search on this site, for example [datasette.io/-/beta?q=fts](https://datasette.io/-/beta?q=fts) - you can read more about how it works in [Building a search engine for datasette.io](https://simonwillison.net/2020/Dec/19/dogsheep-beta/).
