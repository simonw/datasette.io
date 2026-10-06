#!/bin/bash
set -euf -o pipefail

uv run datasette . --port 9008 --reload
