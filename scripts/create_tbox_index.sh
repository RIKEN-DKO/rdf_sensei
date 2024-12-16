
#!/bin/bash

# Usage: ./create_tbox_index.sh <index_t_box> <endpoint_t_box_url> <database>

base_dir="/home/julio/repos/nl2sparql_synthetic_data/data/tabox_index/xsearch_cell"
INDEX_T_BOX=$1
ENDPOINT_T_BOX_URL="https://knowledge.brc.riken.jp/bioresource/sparql"
DATABASE="http://metadb.riken.jp/db/xsearch_cell"

cd rdfsensei/semantic_search
python create_tbox_index.py  --endpoint_t_box_url $ENDPOINT_T_BOX_URL \
    --database $DATABASE \
    --base_dir $base_dir \