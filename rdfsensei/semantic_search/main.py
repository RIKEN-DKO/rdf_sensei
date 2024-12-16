
from data_loader import DataLoader
from embedding_generator import EmbeddingGenerator
from faiss_index import FaissIndex
from query_processor import QueryProcessor
import numpy as np

def main():
    data_directory = 'data'  # Directory where your JSON files are stored

    # Step 1: Load and preprocess data
    data_loader = DataLoader(data_directory)
    data_loader.load_data()
    processed_data = data_loader.preprocess_questions()
    if not processed_data:
        print("No data to process.")
        return

    cleaned_questions, metadata = zip(*processed_data)

    # Step 2: Generate embeddings
    embedding_generator = EmbeddingGenerator()
    embeddings = embedding_generator.generate_embeddings(list(cleaned_questions))

    # Step 3: Build Faiss index
    embedding_dim = embeddings.shape[1]
    faiss_index = FaissIndex(embedding_dim, use_gpu=True)
    faiss_index.build_index(embeddings, list(metadata))

    # Step 4: Initialize Query Processor
    query_processor = QueryProcessor(embedding_generator, faiss_index)

    # Example usage
    user_query = input("Enter your question: ")
    result = query_processor.process_query(user_query)
    if result:
        print("\nMatched Question:\n", result['original_question'])
        print("\nSPARQL Query:\n", result['sparql_query'])
    else:
        print("No similar question found.")

if __name__ == '__main__':
    main()