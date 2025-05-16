#!/bin/bash
set -euf -o pipefail

# Add GitHub Actions runner flyctl to the PATH
export PATH="/home/runner/.fly/bin:$PATH"

datasette publish fly \
  content.db docs-index.db dogsheep-index.db blog.db tils.db \
  --branch 1.0a2 \
  --app datasette-io \
  --template-dir=templates \
  --metadata=metadata.yml \
  --plugins-dir=plugins \
  --static=static:static \
  --install='datasette-render-markdown>=2.2.1' \
  --install=Pygments \
  --install=datasette-template-sql \
  --install=python-dateutil \
  --install=datasette-vega \
  --install=datasette-atom \
  --install=datasette-graphql \
  --install=datasette-json-html \
  --install=datasette-debug-asgi \
  --install=datasette-gzip \
  --install=html5lib \
  --install=beautifulsoup4 \
  --install 'dogsheep-beta>=0.10.1' \
  --install 'httpx==0.27.2' \
  --install datasette-chatgpt-plugin \
  --extra-options '--setting sql_time_limit_ms 2000'
