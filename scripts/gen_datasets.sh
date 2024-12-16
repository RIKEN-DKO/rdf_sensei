#!/bin/bash

cd rdfsensei/datagen
datasource="/home/julio/repos/nl2sparql_synthetic_data/data/xsearch_cell20240822.ttl"
top_n=2
sample_size=2
# Iterate over k values from 3 to 10
for k in {2..3}
do
    echo "Executing with k=$k"
    python generate_dataset_community.py $datasource \
    xcell_path_dataset_rating_${k}.json \
    --use_labels --filter_empty_results --top_n $top_n --sample_size $sample_size \
    --url_endpoint https://knowledge.brc.riken.jp/bioresource/sparql \
    --database http://metadb.riken.jp/db/xsearch_cell --use_riken --k $k
done
