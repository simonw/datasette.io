# datasette.io

The official project website for [Datasette](https://github.com/simonw/datasette).

https://datasette.io/

More background: [datasette.io, an official project website for Datasette](https://simonwillison.net/2020/Dec/13/datasette-io/)

## Development

Check out this repository, create a virtual environment and run `pip install -r requirements.txt` for the dependencies.

If you don't want to build the database files from scratch, run this:

    curl -O https://datasette.io/content.db
    curl -O https://datasette.io/blog.db

To build the database files used by the site:

    scripts/build.sh

Then to run the tests (which check that certain pages do not return errors):

    scripts/test.sh

To see the site in your browser:

    datasette .

This will run a server at `http://localhost:8001/`
