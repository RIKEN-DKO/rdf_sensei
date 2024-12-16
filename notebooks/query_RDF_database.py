# %%
%load_ext autoreload
%autoreload 2

# %%
import os
#Read the key /home/julio/repos/nl2sparql_synthetic_data/data/openai_key.txt
with open('/home/julio/repos/nl2sparql_synthetic_data/data/openai_key.txt', 'r') as file:
    key = file.read().replace('\n', '')
os.environ["OPENAI_API_KEY"]= key

from openai import OpenAI

# %%
# os.chdir('../rdf_sensei')

# %%
from rdfsensei.semantic_search.data_loader import DataLoader
from rdfsensei.semantic_search.embedding_generator import EmbeddingGenerator
from rdfsensei.semantic_search.faiss_index import FaissIndex
from rdfsensei.semantic_search.query_processor import QueryProcessor
import numpy as np
import openai

# %%
# data_directory = '../data/gendata_xcell'  # Directory where your JSON files are stored
data_directory = '/home/julio/repos/nl2sparql_synthetic_data/data/x_cell_small'  # Directory where your JSON files are stored

# Step 1: Load and preprocess data
data_loader = DataLoader(data_directory)
data_loader.load_data()
processed_data = data_loader.preprocess_questions()
if not processed_data:
    print("No data to process.")



# %%

cleaned_questions, metadata = zip(*processed_data)

# Step 2: Generate embeddings
embedding_generator = EmbeddingGenerator()
embeddings = embedding_generator.generate_embeddings(list(cleaned_questions))


# %%

# Step 3: Build Faiss index
embedding_dim = embeddings.shape[1]
faiss_index = FaissIndex(embedding_dim, use_gpu=True)
faiss_index.build_index(embeddings, list(metadata))


# %%
labels_path = "/home/julio/repos/nl2sparql_synthetic_data/data/tabox_index/xsearch_cell/labels.obj"
counts_path = "/home/julio/repos/nl2sparql_synthetic_data/data/tabox_index/xsearch_cell/counts.obj"
endpoint_t_box_url = "https://knowledge.brc.riken.jp/bioresource/sparql"
database="http://metadb.riken.jp/db/xsearch_cell"
path_index = "/home/julio/repos/nl2sparql_synthetic_data/data/tabox_index/xsearch_cell/t_box_index/faiss"
# Step 4: Initialize Query Processor
from riqme.context.LLMStrategies import OpenAIStrategy  # Import your LLM strategy

# Load LLM strategy (can be OpenAI, Llama, etc.)
openai_client = OpenAI()
llm_strategy = OpenAIStrategy(openai_client)

query_processor = QueryProcessor(embedding_generator, 
                                 faiss_index, labels_path, 
                                 counts_path, endpoint_t_box_url, 
                                 database, path_index,llm_strategy=llm_strategy,
                                 model_name='gpt-4o'
                                 )



# %%

# Example usage
# user_query = "Which authority is cited by the cell line"
user_query = "Which cell line references the PubMed article 123d and what is its label?"
results = query_processor.process_query(user_query,top_k_questions=5,do_entity_linking=True)
# if result:
#     print("\nMatched Question:\n", result['original_question'])
#     print("\nSPARQL Query:\n", result['sparql_query'])
# else:
#     print("No similar question found.")
# for result in results['semantic_search']:
#     print("\nMatched Question:\n", result['original_question'])
#     print("\nSPARQL Query:\n", result['sparql_query'])
#     print('Distance:', result['distance'])
#     print('Entity mapping:', result['entity_mapping'])
print("--------SEMANTIC SEARCH--------")
print(results['semantic_search'])
print("--------ENTITY LINKING--------")
print(results['entity_linking'])

# %%
# Example usage
# user_query = "Which authority is cited by the cell line"
user_query = " Which value of HPS0953_culture ?"
results = query_processor.process_query(user_query,top_k_questions=5,do_entity_linking=True)
# if result:
#     print("\nMatched Question:\n", result['original_question'])
#     print("\nSPARQL Query:\n", result['sparql_query'])
# else:
#     print("No similar question found.")
print("Best SPARQL Query:\n", results['best_sparql_query'])
print("--------SEMANTIC SEARCH--------")
for result in results['semantic_search']:
    print("\nMatched Question:\n", result['original_question'])
    print("\nSPARQL Query:\n", result['sparql_query'])
    print('Distance:', result['distance'])
    print('Entity mapping:', result['entity_mapping'])

print("--------ENTITY LINKING--------")
print(results['entity_linking'])
print("--------LLM ANSWER--------")
print(results['llm_answer']['answer'])



