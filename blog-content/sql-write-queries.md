---
title: SQL write queries and stored queries in Datasette 1.0a31
datetime_utc: 2026-05-29 05:14:42
author: Simon Willison
author_url: https://simonwillison.net
---

With [Datasette 1.0a31](https://docs.datasette.io/en/latest/changelog.html#a31-2026-05-28), Datasette now offers users with the necessary permissions the ability to both **execute write queries** against their database and **save stored queries** (renamed from "canned queries"), either privately and shared with other members of their Datasette instance.

Here's an animated demo of the new SQL write interface:

![The user starts on the data database page, selects actions and "Execute write SQL", then selects the insert document template on the next page and executes it with a title of "My document!". Also demonstrates that a create table statement cannot be executed because the user does not have create-table permission.](https://datasette.io/static/blog/2026/sql-write-ui.gif)

Users with the new `execute-write-sql` permission gain an "Execute write SQL" database action. This takes them to a page where they can either enter a SQL query to execute or pick from a set of templates, which provide insert, update and delete queries for tables that they have permission to modify - based on their `insert-row`, `update-row` and `delete-row` permissions.

Datasette analyzes the SQL query and checks which tables it will modify and which relevant Datasette permissions the user needs to have. This works for `create-table` and `alter-table` as well - the full list of permissions can be found [in the documentation](https://docs.datasette.io/en/latest/authentication.html#built-in-actions).

In addition to executing queries directly, Datasette users with the new `store-query` permission can now store both read- and write-queries in the new `queries` table in Datasette's [internal SQLite database](https://docs.datasette.io/en/latest/internals.html#datasette-s-internal-database). You'll need to run Datasette with the `--internal path/to/internal.db` option in order for stored queries to persist across server restarts.

Stored queries can be marked private, in which case they'll only be visible to the user who created them, or they can be shared with other users of the same Datasette instance via Datasette's existing `view-query` permission mechanism.

Learn more:

- The [Datasette 1.0a31 release notes](https://docs.datasette.io/en/latest/changelog.html#a31-2026-05-28)
- Documentation for the [read query, write query and stored query](https://docs.datasette.io/en/latest/pages.html#pages-custom-sql-queries) pages
- Details of the new [Executing write SQL JSON API](https://docs.datasette.io/en/latest/json_api.html#executewriteview)
