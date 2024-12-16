#!/bin/bash

cd synthetiql

k=2

time python generate_dataset_community.py \
/home/julio/Downloads/rdf_bgee \
bgee_path_dataset_rating_${k}.json \
--use_labels \
--filter_empty_results \
--top_n 2 \
--sample_size 2 \
--url_endpoint https://www.bgee.org/sparql/ \
--k $k

