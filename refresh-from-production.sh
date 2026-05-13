#!/bin/bash
set -euf -o pipefail
rm -f blog.db
for f in content.db docs-index.db dogsheep-index.db simon-blog.db tils.db
do
    rm -f $f
    wget -q -O "$f" "https://datasette.io/$f"
    echo $f
done
