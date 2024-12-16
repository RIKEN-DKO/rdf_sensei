import rdflib
import openai
import json
import logging
import re
import os
from rdflib.namespace import RDF
from openai import OpenAI
from path_community_detector import PathCommunityDetector  # Assuming this is in 'community_detector.py'
from prompts import prompt_get_sparqls_from_path_questionsvar_el as prompt_get_sparqls
from prompts import prompt_get_sparqls_from_path_questionsvar_examples as prompt_get_sparqls_examples
from prompts import prompt_rating_questions  # Import the rating prompt
from tqdm import tqdm  # Import tqdm for progress bar
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed

client = OpenAI()

def parse_rdf_file(file_path):
    """
    Function to parse a single RDF file. This will be run in a separate process.
    """
    rdf_format = rdflib.util.guess_format(file_path)
    if rdf_format is None:
        rdf_format = 'xml'  # Default format if unknown
    graph = rdflib.Graph()
    try:
        graph.parse(file_path, format=rdf_format)
        logging.info(f"Parsed RDF file: {file_path}")
        return graph
    except Exception as e:
        logging.warning(f"Failed to parse {file_path}: {e}")
        return None  # Return None if parsing fails


def merge_graphs(graphs):
    merged_graph = rdflib.Graph()
    for g in graphs:
        if g is not None:
            merged_graph += g
    return merged_graph



class GraphDatasetGenerator:
    def __init__(self, graph_source, endpoint, 
                 model_name="gpt-4", use_labels=True, 
                 api_key=None, queries_examples=None,
                 load_parallel=False):
        """
        Initializes the GraphDatasetGenerator.

        Parameters:
        - graph_source: Path to an RDF file or directory containing RDF files.
        - endpoint: SPARQL endpoint instance.
        - model_name: OpenAI model name.
        - use_labels: Whether to use labels in processing.
        - api_key: OpenAI API key.
        - queries_examples: Examples for prompting.
        """
        self.graph_source = graph_source
        self.graph = rdflib.Graph()
        self.endpoint = endpoint  # Use the provided Endpoint instance
        self.model_name = model_name
        self.use_labels = use_labels
        self.api_key = api_key
        # Create an instance of CommunityDetector
        # Initialize OpenAI API key
        openai.api_key = self.api_key
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        # Load the RDF graph(s)
        if load_parallel:
            self._load_graph_parallel()
        else:
            self._load_graph()

        self.detector = PathCommunityDetector(self.graph, use_labels=use_labels)

    def _load_graph(self):
        """
        Private method to load RDF data from a file or directory.
        """
        if os.path.isdir(self.graph_source):
            # Iterate over all files in the directory
            for filename in os.listdir(self.graph_source):
                file_path = os.path.join(self.graph_source, filename)
                if os.path.isfile(file_path):
                    rdf_format = rdflib.util.guess_format(file_path)
                    if rdf_format is None:
                        rdf_format = 'xml'  # Default format if unknown
                    try:
                        self.graph.parse(file_path, format=rdf_format)
                        logging.info(f"Parsed RDF file: {file_path}")
                    except Exception as e:
                        logging.warning(f"Failed to parse {file_path}: {e}")
        elif os.path.isfile(self.graph_source):
            # Single file case
            rdf_format = rdflib.util.guess_format(self.graph_source)
            if rdf_format is None:
                rdf_format = 'xml'  # Default format if unknown
            self.graph.parse(self.graph_source, format=rdf_format)
            logging.info(f"Parsed RDF file: {self.graph_source}")
        else:
            raise ValueError(f"The graph source {self.graph_source} is neither a file nor a directory.")



    def _load_graph_parallel(self):
        file_list = []
        for root, dirs, files in os.walk(self.graph_source):
            for filename in files:
                file_path = os.path.join(root, filename)
                if os.path.isfile(file_path):
                    file_list.append(file_path)

        num_processes = multiprocessing.cpu_count()
        logging.info(f"Parsing RDF files using {num_processes} processes.")

        with ProcessPoolExecutor(max_workers=num_processes) as executor:
            future_to_file = {executor.submit(parse_rdf_file, file_path): file_path for file_path in file_list}
            parsed_graphs = []
            for future in tqdm(as_completed(future_to_file), total=len(future_to_file), desc='Parsing RDF files'):
                file_path = future_to_file[future]
                try:
                    g = future.result()
                    if g is not None:
                        parsed_graphs.append(g)
                except Exception as e:
                    logging.warning(f"Failed to parse {file_path}: {e}")

        #Combine the parsed graphs
        for g in tqdm(parsed_graphs, desc='Combining graphs'):
            self.graph += g

        logging.info(f"Total triples in combined graph: {len(self.graph)}")
        
        # num_processes = multiprocessing.cpu_count()
        # chunk_size = max(1, len(parsed_graphs) // num_processes)
        # graph_chunks = [parsed_graphs[i:i + chunk_size] for i in range(0, len(parsed_graphs), chunk_size)]

        # logging.info(f"Merging parsed graphs using {num_processes} processes.")
        # with multiprocessing.Pool(processes=num_processes) as pool:
        #     merged_graphs = list(tqdm(pool.map(merge_graphs, graph_chunks), total=len(graph_chunks), desc='Merging graphs'))

        # # Merge the merged graphs sequentially
        # self.graph = rdflib.Graph()
        # for mg in tqdm(merged_graphs, desc='Final merging'):
        #     self.graph += mg
        # logging.info(f"Total triples in combined graph: {len(self.graph)}")


    def generate_dataset(self, output_file, 
                         k=2, top_n=10, sample_size=3, 
                         filter_empty_results=True,
                         examples=None):
        # Use the CommunityDetector to find the most common paths
        print("Finding most common paths...")
        output = self.detector.find_most_common_paths(k=k, top_n=top_n, sample_size=sample_size)
        # Generate prompts from the output
        print("Generating prompts...")
        prompts = generate_prompts(output, examples)
        # For each prompt, get the question and SPARQL query
        results = []
        for idx, prompt in enumerate(tqdm(prompts, desc='Processing prompts')):
            logging.info(f"Processing prompt {idx + 1}/{len(prompts)}")
            result_text = get_question_and_sparql(prompt, self.model_name)
            # Parse the response to extract the question and SPARQL query
            response_data = self.parse_openai_response(result_text)
            questions = response_data.get('questions', [])
            sparql_query = response_data.get('sparql_query')
            if questions and sparql_query:
                # Execute the SPARQL query using the Endpoint
                try:
                    query_results = self.endpoint.run_sparql(sparql_query)
                    if filter_empty_results and len(query_results) == 0:
                        # Skip this entry
                        logging.info("Skipping query with empty results.")
                        continue
                    else:
                        # Rate the questions
                        rated_questions = self.rate_questions(questions, sparql_query, query_results)
                        # Add to results
                        results.append({
                            'sample': prompt['sample'],
                            'questions': rated_questions,
                            'sparql_query': sparql_query,
                            'query_results': query_results,
                            'entity_mapping': response_data.get('entity_mapping'),
                            'sparql_template': response_data.get('sparql_template')
                        })
                except Exception as e:
                    logging.warning(f"Error executing SPARQL query: {e}")
                    continue
            else:
                logging.warning("Skipping prompt due to parsing issues.")
                continue

        # Save the results to a JSON file
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logging.info(f"Dataset saved to {output_file}")

        return results
    
    def parse_openai_response(self, response_text):
        questions = []
        sparql_query = None
        entity_mapping = {}
        sparql_template = None

        # Use regular expressions to extract the different parts
        question_match = re.search(r'\*\*question:\*\*\s*(.*?)\s*\*\*SPARQL:\*\*', response_text, re.IGNORECASE | re.DOTALL)
        sparql_match = re.search(r'\*\*SPARQL:\*\*\s*```sparql\s*(.*?)```', response_text, re.IGNORECASE | re.DOTALL)
        entity_mapping_match = re.search(r'\*\*Entity to URI Mapping:\*\*\s*(.*?)\s*\*\*SPARQL Template:\*\*', response_text, re.IGNORECASE | re.DOTALL)
        sparql_template_match = re.search(r'\*\*SPARQL Template:\*\*\s*```sparql\s*(.*?)```', response_text, re.IGNORECASE | re.DOTALL)

        if question_match:
            questions_text = question_match.group(1).strip()
            questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
        else:
            logging.warning("Could not find questions in the response.")
        
        if sparql_match:
            sparql_query = sparql_match.group(1).strip()
        else:
            logging.warning("Could not find SPARQL query in the response.")
        
        if entity_mapping_match:
            entity_mapping_text = entity_mapping_match.group(1).strip()
            for line in entity_mapping_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    entity_mapping[key.strip()] = value.strip()
        else:
            logging.warning("Could not find Entity to URI Mapping in the response.")
        
        if sparql_template_match:
            sparql_template = sparql_template_match.group(1).strip()
        else:
            logging.warning("Could not find SPARQL Template in the response.")

        return {
            'questions': questions,
            'sparql_query': sparql_query,
            'entity_mapping': entity_mapping,
            'sparql_template': sparql_template
        }

    def rate_questions(self, questions, sparql_query,query_results,max_num_results=1):
        data = json.dumps(query_results[:max_num_results], indent=2)

        questions_text = "\n".join([f"{idx + 1}. {q}" for idx, q in enumerate(questions)])
        prompt = prompt_rating_questions.format(data=data,sparql=sparql_query, questions=questions_text)
        # print("DEBUG: Prompt for rating questions")
        # print("Prompt:---------------------\n", prompt)
        response_text = get_question_and_sparql({'prompt': prompt}, self.model_name)
        return self.parse_ratings_response(response_text, questions)

    def parse_ratings_response(self, response_text, questions):
        rated_questions = []
        for idx, question in enumerate(questions):
            rating_match = re.search(rf'Question {idx + 1}:\s*- \*\*Rating\*\*: (\d)', response_text)
            rating = int(rating_match.group(1)) if rating_match else 0
            rated_questions.append({
                'question': question,
                'rating': rating
            })
        return rated_questions


def generate_prompts(output,examples=None):
    prompts = []
    id_to_label = output['id_to_label']
    # Iterate over each path in output['paths']
    for class_path, info in output['top_paths']:
        samples = info['samples']
        # Reconstruct the class path using the input triples
        class_path_description = []
        for s, p, o in class_path:
            class_path_description.append(f"<{s}> <{p}> <{o}> .")
        class_path_str = "\n".join(class_path_description)
        # Iterate over each sample (instance path)
        for sample in samples:
            # Split the instance path and labels
            try:
                instance_path_part, labels_part = sample.strip().split("#LABELS:\n")
                labels_path = labels_part.strip()
            except ValueError:
                instance_path_part = sample.strip()
                labels_path = ""
            # Format the instance path (without labels)
            instance_path = instance_path_part.strip()
            # Combine the class path and instance path with labels into the description
            description = f"Class path:\n{class_path_str}\n\nInstance path:\n{instance_path}\n#LABELS:\n{labels_path}"
            # Create the prompt based on the description
            if examples is None:
                prompt = prompt_get_sparqls.format(description=description)
            else:
                prompt = prompt_get_sparqls_examples.format(description=description,examples=examples)

            # Append the prompt and the sample for reference
            prompts.append({'prompt': prompt, 'sample': sample})

    print(f"Generated {len(prompts)} prompts.")
    print(prompts[0]['prompt'])
    return prompts



# Function to call the OpenAI API and get the question and SPARQL query
def get_question_and_sparql(prompt, model_name="gpt-4o"):


    response = client.chat.completions.create(
        model=model_name,  # Update with the correct model ID if necessary
        messages=[{"role": "user", "content": prompt['prompt']}],
        max_tokens=500,
        temperature=0.7,
        n=1,
        stop=None,
    )
    return response.choices[0].message.content
