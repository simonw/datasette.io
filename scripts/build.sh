#!/bin/bash
set -eu -o pipefail

check_sqlite_db() {
  db_path=$1
  if [ ! -s "$db_path" ]; then
    echo "SQLite database validation failed: $db_path is missing or empty" >&2
    exit 1
  fi
  if ! output=$(sqlite3 "$db_path" 'PRAGMA quick_check;' 2>&1); then
    echo "SQLite database validation failed for $db_path" >&2
    echo "$output" >&2
    exit 1
  fi
  if [ "$output" != "ok" ]; then
    echo "SQLite database validation failed for $db_path" >&2
    echo "$output" >&2
    exit 1
  fi
}

# Populate news database
sqlite-utils content.db 'drop table if exists news'
yaml-to-sqlite content.db news news.yaml

# Populate example_csvs
sqlite-utils content.db 'drop table if exists example_csvs'
yaml-to-sqlite content.db example_csvs example_csvs.yml

# Populate uses table for the /for section
markdown-to-sqlite content.db uses for/*.md

# Populate blog_posts table for the /blog section
python build_blog_posts.py

# Build plugin and tools directories
sqlite-utils drop-table content.db plugin_repos --ignore
sqlite-utils drop-table content.db tool_repos --ignore
yaml-to-sqlite content.db plugin_repos plugin_repos.yml
yaml-to-sqlite content.db tool_repos tool_repos.yml
rm -rf /tmp/stashed-readmes
git clone https://github.com/datasette/stashed-readmes /tmp/stashed-readmes
python build_directory.py content.db /tmp/stashed-readmes --fetch-missing-releases \
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
rm -f blog.db
python fetch_blog_content.py simon-blog.db datasette dogsheep sqliteutils

# Fetch TILs
curl -L -o tils.db https://github.com/simonw/til-db/raw/main/tils.db
check_sqlite_db tils.db

# Fetch global-power-plants.db and legislators.db
curl -L -o global-power-plants.db https://static.simonwillison.net/static/2023/global-power-plants.db
check_sqlite_db global-power-plants.db
if [ "${SKIP_LEGISLATORS_DB_DOWNLOAD:-}" = "1" ]; then
  test -f legislators.db
else
  curl --fail -L -o legislators.db https://datasette.io/legislators.db || \
    curl --fail -L -o legislators.db https://static.simonwillison.net/static/2025/legislators.db
fi
check_sqlite_db legislators.db

# Fetch documentation database for search index
curl -o docs-index.db https://stable-docs.datasette.io/docs.db
check_sqlite_db docs-index.db

# Import stats.json
curl -f -S https://raw.githubusercontent.com/simonw/package-stats/main/stats.json \
  | python build_stats.py content.db -

# Build tutorials table, for search
python index_tutorials.py

# Build search index
dogsheep-beta index dogsheep-index.db templates/dogsheep-beta.yml

# Remove stale entries from before blog.db was renamed to simon-blog.db
sqlite-utils dogsheep-index.db "delete from search_index where type = 'blog.db/entries'"

# Temp hack to remove any rogue tils
sqlite-utils dogsheep-index.db "delete from search_index where type = 'tils.db/til'"

sqlite-utils rebuild-fts dogsheep-index.db
