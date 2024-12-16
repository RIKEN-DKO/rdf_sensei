import re
from typing import Dict
from rdfsensei.semantic_search.embedding_generator import EmbeddingGenerator
from rdfsensei.semantic_search.faiss_index import FaissIndex
from riqme.sparql.EndpointRiken import Endpoint
from riqme.nlp.normalizer import Normalizer
from riqme.index.import_index import TBoxIndex
from riqme.nlp.parsers import parser_sentence
from riqme.context.LLMStrategies import LLMStrategy  # Import your LLM strategy
from rdfsensei.semantic_search.sparql_query_handler import SPARQLQueryHandler

class QueryProcessor:
    def __init__(self, embedding_generator: EmbeddingGenerator, 
                 index: FaissIndex, labels_path: str, counts_path: str,
                   endpoint_t_box_url: str, database: str, path_index: str,
                   llm_strategy, model_name="gpt4o"):
        self.embedding_generator = embedding_generator
        self.index = index
        # Initialize entity linker components
        self.endpoint_t_box = Endpoint(endpoint_t_box_url, database, labels_path, counts_path)
        self.t_box_index = TBoxIndex(self.endpoint_t_box, Normalizer(), path_index=path_index)
        self.question_handler = SPARQLQueryHandler(self.endpoint_t_box, llm_strategy, model_name)

    def process_query(self, query: str, top_k_questions=10,choice_threshold=0.5,do_entity_linking=False) -> Dict:
        # Remove entities marked with <<>>
        cleaned_query = re.sub(r'<<.*?>>', '', query).strip()
        # Generate embedding
        query_embedding = self.embedding_generator.generate_embeddings([cleaned_query])
        # Search in the Faiss index
        results_questions_search = self.index.search(query_embedding, top_k=top_k_questions)

        results = {}

        if results_questions_search:
            # Perform entity linking
            results['semantic_search'] = results_questions_search
            best_sparql_query = results_questions_search[0]['sparql_query']
            results['best_sparql_query'] = best_sparql_query

            # Execute the SPARQL query and get an answer using completions
            print("processing SPARQL query and answer:", query)
            llm_answer = self.question_handler.processQuery(query, best_sparql_query)
            results['llm_answer'] = llm_answer

        #Do entity linking if the bext score is above the threshold
        if results_questions_search[0]['distance'] > choice_threshold or do_entity_linking:
            res_tbox = parser_sentence(query, self.t_box_index, self.endpoint_t_box,
                                       order_by_score=True, return_minimal=True)
        
            results['entity_linking']= res_tbox
        
        return results