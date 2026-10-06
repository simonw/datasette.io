#!/bin/bash
set -euf -o pipefail

uv run python build_blog_posts.py
