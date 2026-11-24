#!/bin/bash
set -euf -o pipefail

# -c datasette.yml is needed because passing any -s option stops Datasette
# from auto-loading datasette.yml from the configuration directory
uv run datasette . -c datasette.yml --port 9008 --reload \
  -s plugins.datasette-io-blog.dev_mode 1 "$@"
