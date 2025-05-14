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
sqlite-utils drop-table content.db plugin_repos --ignore
sqlite-utils drop-table content.db tool_repos --ignore
yaml-to-sqlite content.db plugin_repos plugin_repos.yml
yaml-to-sqlite content.db tool_repos tool_repos.yml
python build_directory.py content.db --fetch-missing-releases \
   --always-fetch-releases-for-repo simonw/datasette-app

# And fetch data from PyPI via the pypi-datasette-packages cache
if [ ! -d /tmp/pypi-datasette-packages ]
then
  git clone https://github.com/simonw/pypi-datasette-packages /tmp/pypi-datasette-packages
else
  (cd /tmp/pypi-datasette-packages && git pull)
fi

args=$(ls /tmp/pypi-datasette-packages/packages/*.json | awk '{print "-f "$0 " \\"}')
# Load that into pypi_packages/pypi_versions/pypi_releases
eval "pypi-to-sqlite content.db $args
--prefix pypi_"

# Fetch my relevant blog content
python fetch_blog_content.py blog.db datasette dogsheep sqliteutils

# Fetch TILs
curl -L -o tils.db https://github.com/simonw/til-db/raw/main/tils.db

# Fetch documentation database for search index
curl -o docs-index.db https://stable-docs.datasette.io/docs.db

# Import stats.json
curl https://raw.githubusercontent.com/simonw/package-stats/main/stats.json \
  | python build_stats.py content.db -

# Build tutorials table, for search
python index_tutorials.py

# Build search index
dogsheep-beta index dogsheep-index.db templates/dogsheep-beta.yml
sqlite-utils rebuild-fts dogsheep-index.db
