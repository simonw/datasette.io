# datasette.io

The official project website for [Datasette](https://github.com/simonw/datasette).

https://datasette.io/

The site is itself a customized installation of Datasette, using custom templates and plugins to implement the site's functionality.

Take a look at [.github/workflows/deploy.yml](https://github.com/simonw/datasette.io/blob/main/.github/workflows/deploy.yml) to see how the site is built and deployed to Google Cloud Run using GitHub Actions.

More background:

- [datasette.io, an official project website for Datasette](https://simonwillison.net/2020/Dec/13/datasette-io/)
- [Building a search engine for datasette.io](https://simonwillison.net/2020/Dec/19/dogsheep-beta/)
- [The Baked Data architectural pattern](https://simonwillison.net/2021/Jul/28/baked-data/)

## Development

Dependencies are managed with [uv](https://docs.astral.sh/uv/). Check out this repository and install them like this:

    uv sync

If you don't want to build the database files from scratch, run this to download them:

    ./refresh-from-production.sh

To build the database files used by the site you will first need to set an environment variable containing a GitHub personal access token. You can create a token at https://github.com/settings/tokens - then set it as the `GITHUB_TOKEN` environment variable like so:

    export GITHUB_TOKEN="token-here"

Now you can build the databases like this:

    uv run scripts/build.sh

Then to run the tests (which check that certain pages do not return errors):

    uv run pytest
    uv run scripts/test.sh

To see the site in your browser:

    ./dev-server.sh

This will run a server at `http://localhost:9008/` in dev mode: the server restarts when plugins or configuration change, and open pages automatically reload when templates, static files or blog posts change.

Dev mode is enabled by the `plugins.datasette-io-blog.dev_mode` setting - see `plugins/dev_mode.py`. To enable it on a server you start yourself, pass `-c datasette.yml` as well, since any `-s` option stops Datasette from loading `datasette.yml` automatically:

    uv run datasette . -c datasette.yml --reload -s plugins.datasette-io-blog.dev_mode 1

### Blog posts

Blog posts live as Markdown files in `blog-content/`. With `./dev-server.sh` running, saving a post rebuilds the `blog_posts` table in `content.db` and reloads the page. Without dev mode, rebuild the table with:

    ./build-blog.sh
