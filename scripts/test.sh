#!/bin/bash
set -euf -o pipefail

# Don't output anything during this script run
exec > /dev/null

function test_path {
  if ! datasette . --get $1
  then
    echo "Test failed to $1" >&2
    exit 1
  fi
}

test_path "/"
test_path "/for"
test_path "/for/exploratory-analysis"
test_path "/plugins"
test_path "/plugins/datasette-cluster-map"
test_path "/plugins/datasette-geojson"
test_path "/tools"
test_path "/tools/shapefile-to-sqlite"
test_path "/news"
test_path "/-/beta"
test_path "/robots.txt"
test_path "/sitemap.xml"
