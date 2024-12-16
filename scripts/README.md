# Generate data
## RIKEN 
```
python generate_dataset_community.py ../data/xsearch_cell20240822.ttl xcell_path_dataset_rating.json --use_labels --filter_empty_results --top_n 5 --sample_size 2 --url_endpoint https://knowledge.brc.riken.jp/bioresource/sparql --database http://metadb.riken.jp/
db/xsearch_cell --use_riken
```
