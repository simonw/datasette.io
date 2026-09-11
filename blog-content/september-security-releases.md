---
title: Datasette 1.0a39 and 0.65.4 security releases
datetime_utc: 2026-09-11 00:04:50
author: Simon Willison
author_url: https://simonwillison.net
---

We have two big security updates for Datasette today - one for the 1.0 alpha series and another for the 0.65.x stable release:

- [1.0a39](https://pypi.org/project/datasette/1.0a39/)
- [0.65.4](https://pypi.org/project/datasette/0.65.4/)

If you are running Datasette instances on the public internet you should **upgrade now**, in particular if you are using a Datasette authentication plugin to protect private data.

These releases bundle a number of different fixes, some reported by external researchers and others found by our own extensive security audit.

The software security ecosystem has been transformed this year by frontier LLMs and coding agents. We plan to continue auditing Datasette with these tools to help us stay ahead of further vulnerabilities.

Most of the issues we are fixing today affect Datasette instances that are hosted on the public internet while providing authenticated users with access to private data. We have already rolled these fixes out to [Datasette Cloud](https://www.datasette.cloud/).
## How we identified and fixed these issues

[Sevban Dönmez](https://github.com/jankesec) submitted several AI-assisted vulnerability reports to the project, which inspired us to run a full audit using a combination of Claude Fable 5.1, GPT-5.6 Sol, and GPT-6 Astra. This is the first time we've run a thorough coding agent security audit. Several rounds of auditing (looking for similar issues to those that were already found) revealed a significant number of problems.

We fixed these on `main`, and then backported selected fixes to the 0.65.x branch so we could release both versions on the same day.

[Alex Garcia](https://alexgarcia.xyz/) and I worked together running and then responding to the audit, working in a shared private repository. For most of the issues we split the work: one of us would create the automated tests highlighting the issue, then the other would implement the fix. This ensured that two separate humans had eyes on each of the issues, in addition to our coding agents running different models.

We are holding back some of the automated tests from the public repo to give people more time to upgrade before we spell out the details of the vulnerabilities described by those tests.
