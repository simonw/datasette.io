#!/bin/bash
for f in content.db docs-index.db dogsheep-index.db blog.db tils.db
do
    rm -f $f
    wget -q "https://datasette.io/$f"
    echo $f
done
