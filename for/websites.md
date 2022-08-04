---
title: Datasette for websites
summary: "Datasette can be used to power dynamic-static websites: sites that run on serverless hosting while providing dynamic data-backed functionality."
order: 7
---

Datasette templates can be used to build custom websites with Datasette under the hood. Examples include the site you are browsing right now.

## [datasette.io](https://datasette.io/)

The official Datasette website runs on top of a customized Datasette instance.

- [datasette.io, an official project website for Datasette](https://simonwillison.net/2020/Dec/13/datasette-io/) talks through the basics of how the site works.
- [Building a search engine for datasette.io](https://simonwillison.net/2020/Dec/19/dogsheep-beta/) explains how the [site search](https://datasette.io/-/beta) works, using the [dogsheep-beta](https://datasette.io/plugins/dogsheep-beta) search plugin.
- [The Baked Data architectural pattern](https://simonwillison.net/2021/Jul/28/baked-data/) describes the Baked Data architecture pattern used by the site, and provides a detailed description of how the build scripts for the site work.
- [github.com/simonw/datasette.io](https://github.com/simonw/datasette.io) has the full source code for the site, including the GitHub Actions workflows that build the databases and deploy them to Google Cloud Run.

## [Niche Museums](https://www.niche-museums.com/)

[www.niche-museums.com](https://www.niche-museums.com/) is a directory of small and niche museums, powered by Datasette. Read [niche-museums.com, powered by Datasette](https://simonwillison.net/2019/Nov/25/niche-museums/) for details, or browse [the code](https://github.com/simonw/museums) on GitHub.

## [til.simonwillison.net](https://til.simonwillison.net/)

Another example of a Datasette-powered website that is deployed by GitHub Actions. Read [Using a self-rewriting README powered by GitHub Actions to track TILs](https://simonwillison.net/2020/Apr/20/self-rewriting-readme/) for details.
