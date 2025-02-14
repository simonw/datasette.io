#!/bin/bash
set -euf -o pipefail

gcloud config set run/region us-central1
gcloud config set project datasette-222320
datasette publish cloudrun \
  content.db docs-index.db dogsheep-index.db blog.db tils.db \
  --branch 1.0a2 \
  --service datasette-io \
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
  --install 'httpx==0.27.2' \ # https://github.com/simonw/datasette.io/issues/161'
  --install datasette-chatgpt-plugin \
  --extra-options '--setting sql_time_limit_ms 2000'
