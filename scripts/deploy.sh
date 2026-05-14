#!/bin/bash
set -euf -o pipefail

# Add GitHub Actions runner flyctl to the PATH
export PATH="/home/runner/.fly/bin:$PATH"

# Copy datasette.yml into templates dir so it gets included in the Docker context
cp datasette.yml templates/datasette.yml

datasette publish fly \
  content.db \
  docs-index.db \
  dogsheep-index.db \
  simon-blog.db \
  tils.db \
  global-power-plants.db \
  legislators.db \
  --branch 1.0a26 \
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
  --install='datasette-atom==0.10a0' \
  --install='datasette-graphql==3.0a1' \
  --install='datasette-referrer-policy==0.1' \
  --install=datasette-json-html \
  --install=datasette-debug-asgi \
  --install=datasette-gzip \
  --install=datasette-cluster-map \
  --install='datasette-turnstile==0.1a3' \
  --install='datasette-ip-rate-limit==0.1a0' \
  --install=html5lib \
  --install=beautifulsoup4 \
  --install='dogsheep-beta>=0.11' \
  --install=httpx \
  --extra-options '--config templates/datasette.yml'
