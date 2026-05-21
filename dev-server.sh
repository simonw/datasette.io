#!/bin/bash
set -euf -o pipefail

uv run --with-requirements requirements.txt datasette . --port 9008 --reload
