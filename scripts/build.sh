#!/bin/bash
set -eu -o pipefail

# Populate news database
sqlite-utils content.db 'drop table if exists news'
yaml-to-sqlite content.db news news.yaml

# Populate example_csvs
sqlite-utils content.db 'drop table if exists example_csvs'
yaml-to-sqlite content.db example_csvs example_csvs.yml

# Populate uses table for the /for section
markdown-to-sqlite content.db uses for/*.md

# Build plugin and tools directories
yaml-to-sqlite content.db plugin_repos plugin_repos.yml --single-column repo
yaml-to-sqlite content.db tool_repos tool_repos.yml --single-column repo
python build_directory.py content.db --fetch-missing-releases \
   --always-fetch-releases-for-repo simonw/datasette-app

# Fetch my relevant blog content
python fetch_blog_content.py blog.db datasette dogsheep sqliteutils

# Fetch TILs
curl -o tils.db https://github.com/simonw/til-db/raw/main/tils.db

# Fetch documentation database for search index
curl -o docs-index.db https://stable-docs.datasette.io/docs.db

# Import stats.json
curl https://raw.githubusercontent.com/simonw/package-stats/main/stats.json \
  | python build_stats.py content.db -

# Build search index
dogsheep-beta index dogsheep-index.db templates/dogsheep-beta.yml
