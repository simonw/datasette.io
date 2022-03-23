---
title: Serverless read-only databases with Datasette
summary: Serverless hosting usually depends on external hosted databases, but Datasette lets you implement the Baked Data pattern to bundle your data with your application code and deploy it to serverless providers.
order: 7
---

Serverless providers such as [Google Cloud Run](https://cloud.google.com/run) and [Vercel](https://vercel.com/) provide robust, scalable, inexpensive hosting for stateless web applications.

Databases are usually provided as separate add-ons to serverless hosting. If your data is static or changes infrequently, Datasette can be used to unlock the benefits of serverless hosting without needing a separate hosted database.

Datasette can be used to implement the [<strong>Baked Data</strong>](https://simonwillison.net/2021/Jul/28/baked-data/) pattern, where any structured data needed by your application is bundled and deployed with the application code itself, as part of the same container.

This site is an example of Baked Data in action: datasette.io is deployed to Google Cloud Run by build scripts running [on GitHub Actions](https://github.com/simonw/datasette.io/blob/main/.github/workflows/deploy.yml).

Many of the [Datasette examples](/examples) listed on this site are also deployed in this manner.
