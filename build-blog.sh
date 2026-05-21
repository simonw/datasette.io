#!/bin/bash
set -euf -o pipefail

uv run --with-requirements requirements.txt python build_blog_posts.py
