---
title: Datasette 1.0a33 with JSON extras in the API
datetime_utc: 2026-06-11 17:26:45
author: Simon Willison
author_url: https://simonwillison.net
---

The stable release of Datasette 1.0 has been in the pipeline for a *long* time. Today's release of [1.0a33](https://docs.datasette.io/en/latest/changelog.html#a33-2026-06-11) incorporates significant progress on one of the key blockers for that release: providing a stable, fully documented JSON API for accessing data hosted in Datasette.

The key problem with the 0.x API is its verbosity: Datasette usually returns more JSON than the client needs, often wasting SQL queries to generate data that is not used.

The `?_extra=` mechanism, first introduced for tables [in Datasette 1.0a3](https://docs.datasette.io/en/latest/changelog.html#a3-2023-08-09), is designed to address that. 1.0a33 extends that pattern to rows and queries. Quoting the [1.0a33 release notes](https://docs.datasette.io/en/latest/changelog.html#a33-2026-06-11):

> **`?_extra=` support for row and query pages**
> 
> Row and query JSON pages now support the same `?_extra=` mechanism as table pages. Row pages can request extras such as `foreign_key_tables`, `query`, `metadata` and `database_color`; arbitrary SQL and stored query pages can request extras such as `columns`, `query`, `metadata` and `private`. The implementation was refactored into a registry of extra classes shared by all three page types.
>
> New generated reference documentation describes every `?_extra=` parameter available on table, row and query JSON pages, with example output captured from a live Datasette instance at documentation build time. See [Expanding JSON responses](https://docs.datasette.io/en/latest/json_api.html#json-api-extra) for the full list.

The minimal default response for a table page such as `/fixtures/facetable.json` in Datasette 1.0 [starts like this](https://latest.datasette.io/fixtures/facetable.json):

```json
{
  "ok": true,
  "next": null,
  "rows": [
    {
      "pk": 1,
      "created": "2019-01-14 08:00:00",
      "planet_int": 1,
      "on_earth": 1,
      "state": "CA",
      "_city_id": 1,
      "_neighborhood": "Mission",
      "tags": "[\"tag1\", \"tag2\"]",
      "complex_array": "[{\"foo\": \"bar\"}]",
      "distinct_some_null": "one",
      "n": "n1"
    }
```

We can add `?_extra=` parameters to request extras. Here's an example that requests several:

[/fixtures/facetable.json?_size=1&_facet=state&_extra=count&_extra=count_sql&_extra=expandable_columns&_extra=facet_results](https://latest.datasette.io/fixtures/facetable.json?_size=1&_facet=state&_extra=count&_extra=count_sql&_extra=expandable_columns&_extra=facet_results)

Which returns this JSON, with each requested extra corresponding to a key in the resulting object:

```json
{
  "ok": true,
  "next": "1",
  "count": 15,
  "count_sql": "select count(*) from facetable ",
  "expandable_columns": [
    [
      {
        "column": "_city_id",
        "other_table": "facet_cities",
        "other_column": "id"
      },
      "name"
    ]
  ],
  "facet_results": {
    "results": {
      "state": {
        "name": "state",
        "type": "column",
        "hideable": true,
        "toggle_url": "/fixtures/facetable.json?_size=1&_extra=count&_extra=count_sql&_extra=expandable_columns&_extra=facet_results",
        "results": [
          {
            "value": "CA",
            "label": "CA",
            "count": 10,
            "toggle_url": "https://latest.datasette.io/fixtures/facetable.json?_size=1&_facet=state&_extra=count&_extra=count_sql&_extra=expandable_columns&_extra=facet_results&state=CA",
            "selected": false
          },
          {
            "value": "MI",
            "label": "MI",
            "count": 4,
            "toggle_url": "https://latest.datasette.io/fixtures/facetable.json?_size=1&_facet=state&_extra=count&_extra=count_sql&_extra=expandable_columns&_extra=facet_results&state=MI",
            "selected": false
          },
          {
            "value": "MC",
            "label": "MC",
            "count": 1,
            "toggle_url": "https://latest.datasette.io/fixtures/facetable.json?_size=1&_facet=state&_extra=count&_extra=count_sql&_extra=expandable_columns&_extra=facet_results&state=MC",
            "selected": false
          }
        ],
        "truncated": false
      }
    },
    "timed_out": [
    ]
  },
  "rows": [
    {
      "pk": 1,
      "created": "2019-01-14 08:00:00",
      "planet_int": 1,
      "on_earth": 1,
      "state": "CA",
      "_city_id": 1,
      "_neighborhood": "Mission",
      "tags": "[\"tag1\", \"tag2\"]",
      "complex_array": "[{\"foo\": \"bar\"}]",
      "distinct_some_null": "one",
      "n": "n1"
    }
  ],
  "truncated": false
}
```

You can explore the full set of available extras in the [Datasette extras API explorer tool](https://tools.simonwillison.net/datasette-extras-explorer):

![Screenshot of a web application titled "Datasette extras explorer". A URL input field contains https://latest.datasette.io/fixtures/facetable.json with a teal Explore button next to it. Below, a left panel labeled EXTRAS (30) lists checkboxes: all_columns - All columns in the table, regardless of _col/_nocol filtering; column_types - Column type assignments for this table; columns (checked) - Column names returned by this query; count - Total count of rows matching these filters; count_sql - SQL query used to calculate the total count; custom_table_templates - Custom template names considered for this table; database - Database name; database_color - Color assigned to the database. A right panel labeled RESPONSE shows GET /fixtures/fac… with Copy JSON and Copy URL buttons, then a dark JSON viewer showing 200 - 9.9 KB - 114ms and JSON: "ok": true, "next": null, "columns": (highlighted array) "pk", "created", "planet_int", "on_earth", "state", "_city_id", "_neighborhood", "tags", "complex_array", "distinct_some_null", "n", "rows": list of objects.](https://datasette.io/static/blog/2026/extras-explorer.png)

Here's that same API explorer for the [query results page](https://tools.simonwillison.net/datasette-extras-explorer#url=https%3A%2F%2Flatest.datasette.io%2Ffixtures%2F-%2Fquery.json%3Fsql%3Dselect%2B*%2Bfrom%2Bfacetable%2Blimit%2B1), and the [individual row page](https://tools.simonwillison.net/datasette-extras-explorer#url=https%3A%2F%2Flatest.datasette.io%2Ffixtures%2Ffacetable%2F1.json).
