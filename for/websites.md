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
- [datasette.io/content](https://datasette.io/content) is the Datasette interface for the main database that powers the site.

## [til.simonwillison.net](https://til.simonwillison.net/)

A blog sharing TILs - Today I Learned snippets.

- [Using a self-rewriting README powered by GitHub Actions to track TILs](https://simonwillison.net/2020/Apr/20/self-rewriting-readme/) introduces the site.
- The site uses the [datasette-atom](https://datasette.io/plugins/datasette-atom) plugin to provide an Atom feed of new entries.
- [til.simonwillison.net/tils](https://til.simonwillison.net/tils) exposes the underlying database.
- The site is deployed to [Vercel](https://vercel.com/) using the [datasette-publish-vercel](https://datasette.io/plugins/datasette-publish-vercel) plugin.

## [Niche Museums](https://www.niche-museums.com/)

[www.niche-museums.com](https://www.niche-museums.com/) is a directory of small and niche museums, powered by Datasette. Read [niche-museums.com, powered by Datasette](https://simonwillison.net/2019/Nov/25/niche-museums/) for details, or browse [the code](https://github.com/simonw/museums) on GitHub.

## [Rocky Beaches](https://www.rockybeaches.com/us/pillar-point)

[Rocky Beaches](https://www.rockybeaches.com/us/pillar-point) by Natalie Downe shows the best times to go tidepooling at Pillar Point near Half Moon Bay, California. It runs on Datasette, using SQL queries to suggest the best times to go based on low tide times and sunrise/sunset and display recent observations recorded on [iNaturalist](https://www.inaturalist.org/).

The source code is available at [github.com/natbat/rockybeaches](https://github.com/natbat/rockybeaches). The site uses the [datasette-graphql](https://datasette.io/plugins/datasette-graphql) in some of the templates, for example [here](https://github.com/natbat/rockybeaches/blob/e072d48479f1404baa206ee660ad228d9f95ac7a/templates/row-data-places.html#L273-L290).
