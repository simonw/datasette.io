---
title: Datasette for publishing data
summary: The built-in "datasette publish" command lets you instantly publish your data to hosting providers like Google Cloud Run, Heroku or Vercel.
order: 2
---

Datasette was [originally inspired](https://simonwillison.net/2018/Aug/19/instantly-publish-datasette/) by work on [the Guardian Data Blog](https://www.theguardian.com/news/datablog/2011/jan/27/data-store-office-for-national-statistics), an initiative to publish the raw data behind the stories in the news.

Datasette encourages sharing data as tables that can be explored by users and exported out as JSON or CSV. It's like publishing a CSV file but with much deeper flexibility for visitors to remix, visualize and export data.

Data published by Datasette can be deployed to both traditional and serverless hosting platforms.

The `datasette publish` command, [documented here](https://docs.datasette.io/en/stable/publish.html), can deploy to [Heroku](https://heroku.com/) and [Google Cloud Run](https://cloud.google.com/run). Plugins can be used to deploy Datasette on [Vercel](https://vercel.com/) or [fly.io](https://fly.io/).

When combined with GitHub Actions, Datasette can be used to automatically deploy new databases on a scheduled basis. See [Deploying a data API using GitHub Actions and Cloud Run](https://simonwillison.net/2020/Jan/21/github-actions-cloud-run/) for more details on implementing this pattern.
